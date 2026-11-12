"""Export labelled native Resolve 21.2 frame grids without moving the playhead.

Use an explicit timeline or MediaPool ID. Frames are 0-based offsets into that
object, NOT absolute record frames. Output is still-image evidence, not playback.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
from resolve_inspect import connect, get_timeline, Reader, digest, write_json


def cut_frames(timeline, track):
    items = sorted([x for x in timeline.GetItemListInTrack('video', track) or []
                    if x.GetType() == 'video'], key=lambda x:x.GetStart())
    origin = timeline.GetStartFrame()
    result = []
    for i, (left, right) in enumerate(zip(items, items[1:]), 1):
        # Capture both actual edges even if a gap is present; don't imply adjacency.
        result.extend([dict(frameOffset=int(left.GetEnd()-origin-1), label=f'{i}: outgoing'),
                       dict(frameOffset=int(right.GetStart()-origin), label=f'{i}: incoming')])
    return result


def find_media(folder, uid):
    found = [m for m in folder.GetClipList() or [] if m.GetMediaId() == uid]
    for sub in folder.GetSubFolderList() or []:
        found.extend(find_media(sub, uid))
    return found


def parse_frames(text):
    result = [int(value.strip()) for value in text.split(',')]
    if not result or any(f < 0 for f in result):
        raise ValueError('Frames must be nonnegative integers.')
    return [dict(frameOffset=f, label=f'offset {f}') for f in result]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument('--timeline-id'); target.add_argument('--media-id')
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument('--frames', help='Comma-separated 0-based offsets, e.g. 0,60,120.')
    selection.add_argument('--cuts', action='store_true', help='Actual video clip edges on --track.')
    parser.add_argument('--track', type=int, default=1)
    parser.add_argument('--per-sheet', type=int, default=6, choices=range(2,13))
    parser.add_argument('--max-dimension', type=int, default=1600)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    if args.output_dir.exists():
        parser.error('Output directory exists; use a fresh review revision.')
    if args.cuts and not args.timeline_id:
        parser.error('--cuts requires --timeline-id.')
    if args.max_dimension < 320 or args.max_dimension > 4096:
        parser.error('--max-dimension must be 320..4096 (whole grid, not each cell).')
    try:
        r, p, declared, _ = connect()
        cls = 'Timeline' if args.timeline_id else 'MediaPoolItem'
        if 'ExportThumbnails' not in declared.get(cls, set()):
            raise RuntimeError('Native ExportThumbnails not declared. Use the documented frame-export fallback.')
        if args.timeline_id:
            obj = get_timeline(p, args.timeline_id)
            if args.cuts and not 1 <= args.track <= obj.GetTrackCount('video'):
                raise ValueError('Video track does not exist.')
            reader = Reader(declared)
            state = reader.timeline(obj)
            if reader.errors:
                raise RuntimeError('Incomplete timeline read-back: '+str(reader.errors))
            length = int(obj.GetEndFrame()-obj.GetStartFrame())
            frames = cut_frames(obj, args.track) if args.cuts else parse_frames(args.frames)
        else:
            matches = find_media(p.GetMediaPool().GetRootFolder(), args.media_id)
            if len(matches) != 1:
                raise ValueError('Media ID not uniquely found in current project.')
            obj = matches[0]
            state = dict(media_id=obj.GetMediaId(), properties=obj.GetClipProperty())
            length = int(state['properties']['Frames'])
            frames = parse_frames(args.frames)
        if not frames or any(f['frameOffset'] >= length for f in frames):
            raise ValueError('Empty selection or frame outside object duration.')
        for f in frames:
            f['label'] += f" | f={f['frameOffset']}"
        active = p.GetCurrentTimeline()
        playhead = active.GetCurrentTimecode() if active else None
        active_id = active.GetUniqueId() if active else None
        args.output_dir.mkdir(parents=True, exist_ok=False)
        report = dict(schema_version='resolve-review-frames/1', resolve_version=r.GetVersionString(),
                      project_id=p.GetUniqueId(), target_id=args.timeline_id or args.media_id,
                      object_type=cls, offsets='0-based relative to target start',
                      state_sha256=digest(state), state=state, frames=frames, sheets=[],
                      review_status={'frames':'exported, inspection pending','motion':'not_checked','listening':'not_checked'})
        for index in range(math.ceil(len(frames)/args.per_sheet)):
            selected = frames[index*args.per_sheet:(index+1)*args.per_sheet]
            path = (args.output_dir/f'frames_{index+1:03}.jpg').resolve()
            result = obj.ExportThumbnails(selected, dict(outputType='file', filePath=str(path),
                                                        maxDimension=args.max_dimension, quality=88))
            report['sheets'].append(dict(file=path.name, frames=selected, result=result))
            if not result or not result.get('success') or not path.is_file() or path.stat().st_size == 0:
                write_json(args.output_dir/'review.json',report)
                raise RuntimeError('Export failed; inspect review.json. Do not claim these frames were checked.')
        current = p.GetCurrentTimeline()
        report['active_timeline_unchanged'] = (current.GetUniqueId() if current else None) == active_id
        report['playhead_unchanged'] = (current.GetCurrentTimecode() if current else None) == playhead
        if args.timeline_id:
            after_reader = Reader(declared)
            after = after_reader.timeline(obj)
            report['state_unchanged'] = not after_reader.errors and digest(after) == report['state_sha256']
        else:
            report['state_unchanged'] = digest(dict(media_id=obj.GetMediaId(), properties=obj.GetClipProperty())) == report['state_sha256']
        write_json(args.output_dir/'review.json', report)
        print(json.dumps(dict(output=str(args.output_dir.resolve()), frames=len(frames),
                              sheets=len(report['sheets']), state_unchanged=report['state_unchanged'])))
        return 0 if all(report[k] for k in ['state_unchanged','playhead_unchanged','active_timeline_unchanged']) else 2
    except Exception as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
