#!/usr/bin/env python3
"""Read-only structural regression checks for Tactical Chronicles stage archives."""
import argparse
import gzip
import hashlib
import json
import re
import sys
from pathlib import Path

BASELINES = {
    'forest-cavern.html.gz': {
        'save_key': 'tap_v14_forest_cavern_escape_ally_visual_polish',
        'preferences': ['tap_v14_grid_display'],
        'min_image_refs': 40,
        'min_uncompressed_bytes': 10_000_000,
        'style_count': 1,
        'enemy_count': 7,
        'min_allies': 2,
    },
    'roster-integration-grounds.html.gz': {
        'save_key': 'tap_roster_integration_v02',
        'preferences': ['tap_roster_grid_display', 'tap_roster_visual_hp'],
        'min_image_refs': 65,
        'min_uncompressed_bytes': 20_000_000,
        'style_count': 2,
        'enemy_count': 8,
        'min_allies': 1,
    },
}

def inspect(path, baseline):
    checks = {}
    try:
        compressed = path.read_bytes()
        raw = gzip.decompress(compressed)
        html = raw.decode('utf-8')
    except (OSError, EOFError, UnicodeError) as exc:
        return {'file': path.name, 'passed': False, 'error': str(exc)}
    def check(name, ok):
        checks[name] = bool(ok)
    check('HTML document', '<html' in html.lower() and '</html>' in html.lower())
    check('Embedded script present', len(re.findall(r'<script\b', html, re.I)) == 1)
    check('Expected style blocks', len(re.findall(r'<style\b', html, re.I)) == baseline['style_count'])
    check('Save identifier preserved', baseline['save_key'] in html)
    for pref in baseline['preferences']:
        check('Preference preserved: '+pref, pref in html)
    for func in ('save', 'load', 'reset', 'render'):
        check('Function exists: '+func, bool(re.search(r'\bfunction\s+'+func+r'\s*\(', html)))
    check('Browser storage calls present', 'localStorage.getItem' in html and 'localStorage.setItem' in html)
    check('Embedded artwork references', html.count('data:image/') >= baseline['min_image_refs'])
    check('Uncompressed size above baseline floor', len(raw) >= baseline['min_uncompressed_bytes'])
    # Checks for characteristic save-loading validation; this is not a runtime save test.
    check('Expected enemy-count guard', bool(re.search(r'enemies\?\.length\s*===\s*'+str(baseline['enemy_count']), html)))
    check('Expected ally-count guard', bool(re.search(r'allies\?\.length\s*>=\s*'+str(baseline['min_allies']), html)))
    return {
        'file': path.name,
        'passed': all(checks.values()),
        'checks': checks,
        'sha256': hashlib.sha256(compressed).hexdigest(),
        'compressed_bytes': len(compressed),
        'uncompressed_bytes': len(raw),
        'embedded_image_references': html.count('data:image/'),
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', nargs='?', default='stages', help='Folder containing .html.gz stage files')
    parser.add_argument('--json', action='store_true', help='Print machine-readable report')
    args = parser.parse_args()
    root = Path(args.directory)
    results = []
    for filename, baseline in BASELINES.items():
        path = root / filename
        if not path.is_file():
            results.append({'file': filename, 'passed': False, 'error': 'File not found'})
        else:
            results.append(inspect(path, baseline))
    passed = all(r['passed'] for r in results)
    if args.json:
        print(json.dumps({'passed': passed, 'results': results}, indent=2))
    else:
        for result in results:
            print(('PASS' if result['passed'] else 'FAIL') + ': ' + result['file'])
            if 'error' in result:
                print('  ERROR: ' + result['error'])
            for name, ok in result.get('checks', {}).items():
                print('  ' + ('OK  ' if ok else 'FAIL') + ' ' + name)
        print('OVERALL:', 'PASS' if passed else 'FAIL')
    return 0 if passed else 1

if __name__ == '__main__':
    sys.exit(main())
