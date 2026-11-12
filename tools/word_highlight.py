"""Offline Word Highlight holder installer for DaVinci Resolve DRT timeline exports.

Verified format: Resolve Studio 21.1.2.10, Windows, 2026-11-02.
This utility does NOT connect to Resolve or generate subtitles. Import the output
DRT through Resolve's scripting API, then re-export and inspect before trusting it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
import zlib
from pathlib import Path
from xml.etree import ElementTree as ET

HERE = Path(__file__).resolve().parent
DEFAULT_ASSET = HERE.parent / 'assets' / 'word_highlight.xml'
# Original native Word Highlight defaults (independent of the donor asset palette).
# Override them explicitly with --normal / --highlight for a requested design.
DEFAULT_NORMAL_COLOR = '#FFEB85'
DEFAULT_HIGHLIGHT_COLOR = '#FF0000'
PRESET = b'TEMPLATES/EDIT/TITLES/SUBTITLES/ANIMATED/WORD HIGHLIGHT'
CHANNELS = {
    'normal': ('Red1', 'Green1', 'Blue1'),
    'highlight': ('HighlightColorRed', 'HighlightColorGreen', 'HighlightColorBlue'),
}
SUBTITLE_RE = re.compile(rb'<SubtitleTrackVec>.*?</SubtitleTrackVec>', re.S)
HOLDER_RE = re.compile(rb'<FusionCompHolderItems>.*?</FusionCompHolderItems>', re.S)
COMPOSITION_RE = re.compile(rb'(<CompositionBA>)([0-9A-Fa-f]+)(</CompositionBA>)', re.S)


class FormatError(ValueError):
    """DRT or Fusion composition is not in the verified format."""


def exact_zlib(data: bytes) -> bytes:
    decoder = zlib.decompressobj()
    try:
        value = decoder.decompress(data) + decoder.flush()
    except zlib.error as exc:
        raise FormatError(f'Invalid zlib stream: {exc}') from exc
    if not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:
        raise FormatError('Zlib stream is incomplete or contains trailing bytes')
    if len(data) < 6 or int.from_bytes(data[-4:], 'big') != zlib.adler32(value):
        raise FormatError('Zlib Adler-32 mismatch')
    return value


def decode_fusion(raw: bytes) -> dict:
    if len(raw) < 10:
        raise FormatError('Fusion CompositionBA is too short')
    outer = exact_zlib(raw[4:])
    if len(outer) != int.from_bytes(raw[:4], 'big'):
        raise FormatError('Outer length header mismatch')
    if len(outer) < 146 or int.from_bytes(outer[142:146], 'big') != len(outer) - 146:
        raise FormatError('Embedded outer length header mismatch (offset 142)')
    if PRESET.lower() not in outer.lower():
        raise FormatError('Not a Word Highlight Fusion composition')
    valid = []
    for marker in re.finditer(rb'\x78\xda', outer):
        offset = marker.start()
        if offset < 4:
            continue
        try:
            inner = exact_zlib(outer[offset:])
        except FormatError:
            continue
        if int.from_bytes(outer[offset-4:offset], 'little') == len(inner):
            valid.append((offset, inner))
    if len(valid) != 1:
        raise FormatError(f'Expected exactly one valid inner Fusion stream, found {len(valid)}')
    offset, inner = valid[0]
    return {'raw': raw, 'outer': outer, 'inner': inner, 'offset': offset}


def encode_fusion(decoded: dict, new_inner: bytes) -> bytes:
    """Rebuild both zlib layers and ALL THREE size headers."""
    outer = decoded['outer']
    offset = decoded['offset']
    updated = (outer[:offset-4]
               + len(new_inner).to_bytes(4, 'little')
               + zlib.compress(new_inner, 9))
    updated = updated[:142] + (len(updated)-146).to_bytes(4, 'big') + updated[146:]
    result = len(updated).to_bytes(4, 'big') + zlib.compress(updated, 6)
    check = decode_fusion(result)
    if check['inner'] != new_inner:
        raise FormatError('Fusion round-trip changed inner macro data')
    return result


def parse_hex(value: str) -> tuple[int, int, int]:
    if not re.fullmatch(r'#[0-9A-Fa-f]{6}', value):
        raise ValueError(f'Expected #RRGGBB, got {value!r}')
    return tuple(int(value[i:i+2], 16) for i in (1, 3, 5))


def input_pattern(name: str) -> re.Pattern[bytes]:
    return re.compile(rb'\b' + name.encode('ascii')
                      + rb'\s*=\s*Input\s*\{\s*Value\s*=\s*([^,}]+),\s*\}')


def current_input(inner: bytes, name: str) -> float | None:
    match = input_pattern(name).findall(inner)
    if len(match) > 1:
        raise FormatError(f'Multiple {name} inputs found')
    if not match:
        return None
    try:
        return float(match[0].strip())
    except ValueError as exc:
        raise FormatError(f'{name} is not numeric') from exc


def set_colors(inner: bytes, normal: str, highlight: str) -> bytes:
    """Change known explicit color inputs only; omitted Red1 default is 1.0.

    Adding a previously absent Input has NOT yet been independently verified.
    Refuse unsupported combinations instead of generating a corrupt timeline.
    """
    if b'Tools = ordered() { Template = TextPlus' not in inner:
        raise FormatError('Cannot locate verified Template = TextPlus structure')
    updated = inner
    for color_type, hex_value in (('normal', normal), ('highlight', highlight)):
        for name, eight_bit in zip(CHANNELS[color_type], parse_hex(hex_value)):
            desired = eight_bit / 255
            found = current_input(updated, name)
            if found is None:
                if name == 'Red1' and eight_bit == 255:
                    continue  # Verified implicit normal-text red default.
                raise FormatError(
                    f'Missing input {name}, requested {desired:.6g}. '
                    'Inserting absent Fusion inputs is not yet verified; stop safely.')
            if abs(found-desired) < 1e-12:
                continue  # Preserve original text and compression where possible.
            expression = input_pattern(name)
            if len(expression.findall(updated)) != 1:
                raise FormatError(f'Cannot uniquely identify input {name}')
            updated = expression.sub(
                lambda m: m.group(0).replace(m.group(1), format(desired, '.15g').encode('ascii')),
                updated, count=1)
            if abs(current_input(updated, name)-desired) >= 1e-12:
                raise FormatError(f'Failed to write {name}')
    return updated


def holder_comp(holder: bytes) -> tuple[re.Match[bytes], bytes]:
    try:
        root = ET.fromstring(holder)
    except ET.ParseError as exc:
        raise FormatError('Holder XML is invalid') from exc
    if root.tag != 'FusionCompHolderItems' or len(root) != 1:
        raise FormatError('Expected a single Word Highlight holder item')
    matches = list(COMPOSITION_RE.finditer(holder))
    if len(matches) != 1:
        raise FormatError('Expected exactly one CompositionBA')
    return matches[0], bytes.fromhex(matches[0].group(2).decode('ascii'))


def recolor_holder(holder: bytes, normal: str, highlight: str) -> bytes:
    match, raw = holder_comp(holder)
    decoded = decode_fusion(raw)
    changed_inner = set_colors(decoded['inner'], normal, highlight)
    changed_raw = raw if changed_inner == decoded['inner'] else encode_fusion(decoded, changed_inner)
    replacement = changed_raw.hex().encode('ascii')
    result = holder[:match.start(2)] + replacement + holder[match.end(2):]
    _, verified = holder_comp(result)
    if decode_fusion(verified)['inner'] != changed_inner:
        raise FormatError('Holder failed self-verification')
    return result


def subtitle_section(seq: bytes) -> tuple[re.Match[bytes], ET.Element]:
    found = list(SUBTITLE_RE.finditer(seq))
    if len(found) != 1:
        raise FormatError(f'Expected one SubtitleTrackVec, found {len(found)}')
    try:
        root = ET.fromstring(found[0].group())
    except ET.ParseError as exc:
        raise FormatError('SubtitleTrackVec XML is invalid') from exc
    tracks = root.findall('./Element/Sm2TiTrack')
    if len(tracks) != 1:
        raise FormatError(f'Expected exactly one subtitle track, found {len(tracks)}')
    return found[0], tracks[0]


def insert_holder(seq: bytes, holder: bytes) -> tuple[bytes, int]:
    area, track = subtitle_section(seq)
    clips = track.find('Items')
    if clips is None:
        raise FormatError('Subtitle track has no Items element')
    current = track.find('FusionCompHolderItems')
    if current is not None and len(current):
        raise FormatError('Destination subtitle track already contains an effect; refusing overwrite')
    section = area.group()
    if HOLDER_RE.search(section):
        # A nonempty tag can be replaced only when ET confirmed zero children.
        section, count = HOLDER_RE.subn(lambda _: holder, section)
        if count != 1:
            raise FormatError(f'Expected one empty holder tag, found {count}')
    elif re.search(rb'<FusionCompHolderItems\s*/>', section):
        section, count = re.subn(rb'<FusionCompHolderItems\s*/>', lambda _: holder, section)
        if count != 1:
            raise FormatError('Ambiguous empty FusionCompHolderItems')
    else:
        anchor = b'</Sm2TiTrack>'
        if section.count(anchor) != 1:
            raise FormatError('Cannot safely insert Fusion holder into track')
        section = section.replace(anchor, holder + b'\n' + anchor)
    updated = seq[:area.start()] + section + seq[area.end():]
    _, test_track = subtitle_section(updated)
    item = test_track.find('FusionCompHolderItems')
    if item is None or len(item) != 1 or len(test_track.find('Items')) != len(clips):
        raise FormatError('Post-insertion track or caption count mismatch')
    found = HOLDER_RE.findall(updated)
    if len(found) != 1:
        raise FormatError('Post-insertion holder count mismatch')
    _, new_raw = holder_comp(found[0])
    decode_fusion(new_raw)
    return updated, len(clips)


def read_archive(path: Path) -> tuple[list[zipfile.ZipInfo], dict[str, bytes], str]:
    with zipfile.ZipFile(path, 'r') as archive:
        if archive.testzip() is not None:
            raise FormatError('DRT ZIP CRC check failed')
        infos = archive.infolist()
        members = {info.filename: archive.read(info.filename) for info in infos}
    seq = [n for n in members if n.startswith('SeqContainer/') and n.endswith('.xml')]
    if len(seq) != 1:
        raise FormatError(f'Expected one sequence XML, found {len(seq)}')
    return infos, members, seq[0]


def install(src: Path, dst: Path, asset: Path, normal: str, highlight: str) -> dict:
    if not src.is_file():
        raise FileNotFoundError(src)
    if not asset.is_file():
        raise FileNotFoundError(asset)
    if dst.exists() or src.resolve() == dst.resolve():
        raise FileExistsError(f'Refusing to overwrite destination: {dst}')
    raw_holder = asset.read_bytes().strip()
    colored = recolor_holder(raw_holder, normal, highlight)
    infos, members, seq_name = read_archive(src)
    before = members[seq_name]
    changed, caption_count = insert_holder(before, colored)
    members[seq_name] = changed
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        with zipfile.ZipFile(dst, 'x') as archive:
            for info in infos:
                archive.writestr(info, members[info.filename])
        _, check, check_seq = read_archive(dst)
        if check_seq != seq_name or check[seq_name] != changed:
            raise FormatError('DRT ZIP round-trip mismatch')
        if any(check[n] != members[n] for n in members):
            raise FormatError('Other DRT archive members were modified')
    except BaseException:
        dst.unlink(missing_ok=True)
        raise
    return {
        'status': 'created_offline_not_imported',
        'source': str(src), 'output': str(dst), 'asset': str(asset),
        'normal': normal.upper(), 'highlight': highlight.upper(),
        'caption_count_preserved': caption_count,
        'holder_sha256': hashlib.sha256(colored).hexdigest(),
        'output_sha256': hashlib.sha256(dst.read_bytes()).hexdigest(),
    }


def inspect_asset(asset: Path) -> dict:
    holder = asset.read_bytes().strip()
    _, raw = holder_comp(holder)
    decoded = decode_fusion(raw)
    return {
        'asset': str(asset), 'holder_bytes': len(holder),
        'holder_sha256': hashlib.sha256(holder).hexdigest(),
        'outer_uncompressed_bytes': len(decoded['outer']),
        'embedded_outer_length': int.from_bytes(decoded['outer'][142:146], 'big'),
        'inner_uncompressed_bytes': len(decoded['inner']),
        'inputs': {name: current_input(decoded['inner'], name)
                   for names in CHANNELS.values() for name in names},
        'zlib_headers_and_checksums_valid': True,
    }


def inspect_drt(path: Path, expect_normal: str | None = None,
                expect_highlight: str | None = None) -> dict:
    """Independently validate an exported/imported DRT, including RGB channels."""
    _, members, seq_name = read_archive(path)
    _, track = subtitle_section(members[seq_name])
    items = track.find('Items')
    effect = track.find('FusionCompHolderItems')
    if items is None or effect is None or len(effect) != 1:
        raise FormatError('Expected one subtitle track containing exactly one effect holder')
    xml_holders = HOLDER_RE.findall(members[seq_name])
    if len(xml_holders) != 1:
        raise FormatError('Cannot uniquely locate Word Highlight holder in DRT XML')
    _, raw = holder_comp(xml_holders[0])
    decoded = decode_fusion(raw)
    colors = {}
    for name, channels in CHANNELS.items():
        parts = []
        for channel in channels:
            value = current_input(decoded['inner'], channel)
            if value is None and channel == 'Red1':
                value = 1.0
            if value is None or not 0.0 <= value <= 1.0:
                raise FormatError(f'Unknown/invalid {channel} input in inspected DRT')
            parts.append(max(0, min(255, round(value * 255))))
        colors[name] = '#' + ''.join(f'{part:02X}' for part in parts)
    if expect_normal and colors['normal'] != expect_normal.upper():
        raise FormatError(f'Normal text color mismatch: {colors["normal"]} != {expect_normal}')
    if expect_highlight and colors['highlight'] != expect_highlight.upper():
        raise FormatError(f'Highlight color mismatch: {colors["highlight"]} != {expect_highlight}')
    return {
        'path': str(path), 'subtitle_tracks': 1, 'subtitle_clips': len(items),
        'fusion_holders': len(effect), 'colors': colors,
        'inner_uncompressed_bytes': len(decoded['inner']),
        'outer_uncompressed_bytes': len(decoded['outer']),
        'embedded_outer_length': int.from_bytes(decoded['outer'][142:146], 'big'),
        'full_zlib_streams_headers_and_checksums_valid': True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    inspect = commands.add_parser('inspect', help='Validate the standalone holder asset')
    inspect.add_argument('--asset', type=Path, default=DEFAULT_ASSET)
    scan = commands.add_parser('inspect-drt', help='Verify Word Highlight and colors in a timeline DRT')
    scan.add_argument('--input', required=True, type=Path)
    scan.add_argument('--expect-normal', default=None)
    scan.add_argument('--expect-highlight', default=None)
    create = commands.add_parser('install', help='Insert Word Highlight into an existing DRT subtitle track')
    create.add_argument('--input', required=True, type=Path)
    create.add_argument('--output', required=True, type=Path)
    create.add_argument('--asset', type=Path, default=DEFAULT_ASSET)
    create.add_argument('--normal', default=DEFAULT_NORMAL_COLOR,
                        help=f'Normal subtitle text color, default {DEFAULT_NORMAL_COLOR}')
    create.add_argument('--highlight', default=DEFAULT_HIGHLIGHT_COLOR,
                        help=f'Active word highlight color, default {DEFAULT_HIGHLIGHT_COLOR}')
    args = parser.parse_args()
    try:
        if args.command == 'inspect':
            result = inspect_asset(args.asset)
        elif args.command == 'inspect-drt':
            result = inspect_drt(args.input, args.expect_normal, args.expect_highlight)
        else:
            result = install(args.input, args.output, args.asset, args.normal, args.highlight)
    except (ValueError, OSError, zipfile.BadZipFile) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
