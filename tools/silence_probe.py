"""Read-only FFmpeg silence interval scanner; source seconds, not Resolve frames.

Local helper in Resolve Agent v1.6; does not open Resolve or edit source media.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

SILENCE_START = re.compile(r"silence_start:\s*([0-9]+(?:\.[0-9]+)?)")
SILENCE_END = re.compile(
    r"silence_end:\s*([0-9]+(?:\.[0-9]+)?)\s*\|\s*silence_duration:\s*([0-9]+(?:\.[0-9]+)?)"
)


def scan_silence(source: Path, noise_db: float, min_silence: float, ffmpeg: str) -> dict:
    """Return detected low-volume intervals from the first audio stream."""
    if not source.is_file():
        raise FileNotFoundError(f"Media file not found: {source}")
    if not (-100 <= noise_db <= 0):
        raise ValueError("noise-db must be between -100 and 0")
    if min_silence <= 0:
        raise ValueError("min-silence must be positive")
    executable = shutil.which(ffmpeg)
    if not executable:
        raise FileNotFoundError(f"ffmpeg executable not found: {ffmpeg}")
    cmd = [
        executable, "-hide_banner", "-nostdin", "-i", str(source),
        "-map", "0:a:0", "-vn", "-af",
        f"silencedetect=noise={noise_db:g}dB:d={min_silence:g}",
        "-f", "null", "-",
    ]
    process = subprocess.run(cmd, capture_output=True, text=True, errors="replace", check=False)
    if process.returncode != 0:
        detail = process.stderr[-1600:].strip()
        raise RuntimeError(f"ffmpeg failed (exit {process.returncode}): {detail}")
    intervals = []
    pending_start = None
    for line in process.stderr.splitlines():
        if match := SILENCE_START.search(line):
            pending_start = float(match.group(1))
        if match := SILENCE_END.search(line):
            end = float(match.group(1))
            duration = float(match.group(2))
            start = pending_start if pending_start is not None else max(0.0, end - duration)
            if end >= start:
                intervals.append({
                    "start_seconds": round(start, 6),
                    "end_seconds": round(end, 6),
                    "duration_seconds": round(end - start, 6),
                })
            pending_start = None
    return {
        "source_file": str(source.resolve()),
        "source_size_bytes": source.stat().st_size,
        "time_reference": "source file stream seconds (not Resolve timeline frames)",
        "parameters": {"noise_db": noise_db, "min_silence_seconds": min_silence},
        "silences": intervals,
        "incomplete_final_interval": pending_start is not None,
        "warning": "Acoustic low-level intervals are not guaranteed speech edit boundaries.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--noise-db", type=float, default=-35.0)
    parser.add_argument("--min-silence", type=float, default=0.35)
    parser.add_argument("--ffmpeg", default="ffmpeg")
    parser.add_argument("--output", type=Path, help="Optional JSON output path")
    args = parser.parse_args(argv)
    try:
        result = scan_silence(args.source, args.noise_db, args.min_silence, args.ffmpeg)
        payload = json.dumps(result, ensure_ascii=False, indent=2)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(payload + "\n", encoding="utf-8")
        else:
            print(payload)
        return 0
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
