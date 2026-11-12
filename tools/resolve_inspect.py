"""Read-only Resolve inventory and field-by-field snapshot comparison.

Python 3.10+, standard library only. Tested on Windows / Resolve Studio 21.2.0.5.
No edits, saves, reloads, imports or timeline selection. Unknown fields stay unknown.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import sys
from datetime import datetime, timezone


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Do not silently replace earlier evidence.
    with path.open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write('\n')


def connect():
    root = os.environ.get('RESOLVE_SCRIPT_API')
    candidates = [Path(root)] if root else []
    candidates += [Path(os.environ.get('PROGRAMDATA', 'C:/ProgramData')) /
                   'Blackmagic Design/DaVinci Resolve/Support/Developer/Scripting']
    api = next((p for p in candidates if (p / 'Modules/DaVinciResolveScript.py').is_file()), None)
    if api is None:
        raise RuntimeError('Set RESOLVE_SCRIPT_API to the installed Developer/Scripting directory.')
    pyi = api / 'DaVinciResolveScript.pyi'
    if not pyi.is_file():
        raise RuntimeError('Installed DaVinciResolveScript.pyi required; no method guessing.')
    tree = ast.parse(pyi.read_text(encoding='utf-8-sig'))
    declared = {c.name: {f.name for f in c.body if isinstance(f, ast.FunctionDef)}
                for c in tree.body if isinstance(c, ast.ClassDef)}
    sys.path.insert(0, str(api / 'Modules'))
    import DaVinciResolveScript as dvr
    resolve = dvr.scriptapp('Resolve')
    if resolve is None:
        raise RuntimeError('No Resolve connection. Check running Studio and scripting access.')
    project = resolve.GetProjectManager().GetCurrentProject()
    if project is None:
        raise RuntimeError('Open the intended Resolve project first.')
    return resolve, project, declared, pyi


def get_timeline(project, timeline_id):
    matches = [project.GetTimelineByIndex(i) for i in range(1, project.GetTimelineCount() + 1)
               if project.GetTimelineByIndex(i).GetUniqueId() == timeline_id]
    if len(matches) != 1:
        raise RuntimeError('Timeline ID not uniquely present in the current project.')
    return matches[0]


class Reader:
    def __init__(self, declared):
        self.declared, self.errors = declared, []

    def read(self, obj, cls, method, *args, location=''):
        if method not in self.declared.get(cls, set()):
            self.errors.append({'location': location, 'method': method, 'error': 'not declared'})
            return None
        try:
            return getattr(obj, method)(*args)
        except Exception as exc:
            self.errors.append({'location': location, 'method': method, 'error': str(exc)})
            return None

    def item(self, x):
        uid, kind = x.GetUniqueId(), x.GetType()
        def read(method, *args):
            return self.read(x, 'TimelineItem', method, *args, location=uid)
        result = dict(id=uid, name=x.GetName(), type=kind,
                      start=read('GetStart', True), end=read('GetEnd', True),
                      duration=read('GetDuration', True), properties=read('GetProperties'))
        if not isinstance(result['properties'], dict):
            self.errors.append({'location':uid, 'method':'GetProperties', 'error':'unknown properties'})
        if kind == 'transition':
            result['transition'] = {k: (result['properties'] or {}).get(k) for k in
                                    ['TransitionType', 'TransitionCategory',
                                     'TransitionDuration', 'TransitionAlignment']}
            return result
        media = read('GetMediaPoolItem')
        linked = read('GetLinkedItems')
        if linked is None:
            self.errors.append({'location':uid, 'method':'GetLinkedItems', 'error':'unknown links'})
        result.update(media_id=media.GetMediaId() if media else None,
                      path=media.GetClipProperty('File Path') if media else None,
                      source_in=read('GetSourceStartFrame'), source_out=read('GetSourceEndFrame'),
                      source_start_seconds=read('GetSourceStartTime'),
                      source_end_seconds=read('GetSourceEndTime'),
                      left_handle=read('GetLeftOffset', True), right_handle=read('GetRightOffset', True),
                      speed=read('GetSpeed'), fades=read('GetFades'), enabled=read('GetClipEnabled'),
                      links=sorted(z.GetUniqueId() for z in linked) if linked is not None else None)
        if kind == 'video':
            result['auto_color_enabled'] = read('GetAutoColorEnabled')
            result['fusion_comp_count'] = read('GetFusionCompCount')
        return result

    def timeline(self, t):
        tracks = []
        for kind in ['video', 'audio', 'subtitle']:
            for index in range(1, t.GetTrackCount(kind) + 1):
                raw = self.read(t, 'Timeline', 'GetItemListInTrack', kind, index, location=t.GetUniqueId())
                if raw is None:
                    self.errors.append({'location':t.GetUniqueId(), 'method':'GetItemListInTrack',
                                        'error':f'unknown items on {kind}{index}'})
                tracks.append(dict(kind=kind, index=index, name=t.GetTrackName(kind, index),
                                   enabled=t.GetIsTrackEnabled(kind, index),
                                   items=[self.item(x) for x in raw] if raw is not None else None))
        return dict(id=t.GetUniqueId(), name=t.GetName(), start=t.GetStartFrame(), end=t.GetEndFrame(),
                    settings=self.read(t, 'Timeline', 'GetSettings'), markers=t.GetMarkers(), tracks=tracks)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(',', ':'), allow_nan=False).encode('utf-8')).hexdigest()


def capture(project, declared, timeline_id=None):
    reader = Reader(declared)
    timelines = [get_timeline(project, timeline_id)] if timeline_id else [
        project.GetTimelineByIndex(i) for i in range(1, project.GetTimelineCount() + 1)]
    media = []
    def visit(folder, prefix=''):
        path = prefix + '/' + folder.GetName()
        for m in folder.GetClipList() or []:
            props = m.GetClipProperty()
            file_path = props.get('File Path')
            media.append(dict(id=m.GetMediaId(), bin=path, name=m.GetName(),
                              properties=props, file_exists=Path(file_path).is_file() if file_path else None))
        for sub in folder.GetSubFolderList() or []:
            visit(sub, path)
    visit(project.GetMediaPool().GetRootFolder())
    state = dict(project_id=project.GetUniqueId(), project_name=project.GetName(),
                 project_settings=reader.read(project, 'Project', 'GetSettings'),
                 media=sorted(media, key=lambda x:x['id']),
                 timelines=[reader.timeline(t) for t in timelines])
    return dict(schema_version='resolve-inspect/1', captured_utc=datetime.now(timezone.utc).isoformat(),
                scope='Native clip structure/properties, media, settings, markers; not full Fusion/Color graphs, '
                      'automation curves, project database, playback or perceptual QA.',
                state=state, state_sha256=digest(state), read_errors=reader.errors)


def differences(a, b, path='$'):
    if type(a) != type(b):
        return [dict(path=path, before=a, after=b)]
    if isinstance(a, dict):
        result = []
        for key in sorted(a.keys() | b.keys()):
            if key not in a or key not in b:
                result.append(dict(path=f'{path}.{key}', before=a.get(key), after=b.get(key),
                                   missing='before' if key not in a else 'after'))
            else:
                result.extend(differences(a[key], b[key], f'{path}.{key}'))
        return result
    if isinstance(a, list):
        result = []
        for index in range(max(len(a), len(b))):
            if index >= len(a) or index >= len(b):
                result.append(dict(path=f'{path}[{index}]', before=a[index] if index < len(a) else None,
                                   after=b[index] if index < len(b) else None))
            else:
                result.extend(differences(a[index], b[index], f'{path}[{index}]'))
        return result
    return [] if a == b else [dict(path=path, before=a, after=b)]


def compare(a, b):
    if a.get('schema_version') != 'resolve-inspect/1' or b.get('schema_version') != 'resolve-inspect/1':
        raise ValueError('Expected resolve-inspect/1 snapshots.')
    # Usage counts can refresh when selecting/reopening a timeline; show them
    # separately instead of treating them as an edit. Never suppress other changes.
    changes = differences(a['state'], b['state'])
    observations = [x for x in changes if x['path'].startswith('$.media[')
                    and x['path'].endswith('.properties.Usage')]
    changes = [x for x in changes if x not in observations]
    errors = a.get('read_errors', []) + b.get('read_errors', [])
    return dict(schema_version='resolve-compare/1', equal=not changes and not errors,
                status='incomplete' if errors else ('different' if changes else 'equal'),
                before_sha256=digest(a['state']), after_sha256=digest(b['state']),
                changes=changes, observations=observations, read_errors=errors,
                limit='Equality only covers the captured fields; no perceptual or full graph guarantee.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    snap = sub.add_parser('snapshot')
    snap.add_argument('--timeline-id', help='Optional exact ID; default captures all timelines.')
    snap.add_argument('--output', type=Path, required=True)
    diff = sub.add_parser('compare')
    diff.add_argument('before', type=Path); diff.add_argument('after', type=Path)
    diff.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Output already exists; use a new revision filename.')
    try:
        if args.command == 'snapshot':
            r, p, declared, pyi = connect()
            value = capture(p, declared, args.timeline_id)
            value.update(resolve_version=r.GetVersionString(), api_path=str(pyi),
                         api_sha256=hashlib.sha256(pyi.read_bytes()).hexdigest())
            code = 2 if value['read_errors'] else 0
        else:
            value = compare(json.loads(args.before.read_text(encoding='utf-8')),
                            json.loads(args.after.read_text(encoding='utf-8')))
            code = 0 if value['equal'] else 2
        write_json(args.output, value)
        print(json.dumps({'output':str(args.output.resolve()), 'status':value.get('status', 'captured'),
                          'read_errors':len(value.get('read_errors', []))}))
        return code
    except Exception as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
