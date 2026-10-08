"""Source integration tests. These do not execute the SRHD engine."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1] / 'tools'
spec = importlib.util.spec_from_file_location('overlay', TOOLS / 'prepare_race_overlay.py')
overlay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(overlay)


class OverlayTests(unittest.TestCase):
    def test_ambiguous_hook_is_rejected(self):
        for source in ['absent', 'hook hook']:
            with self.assertRaises(ValueError):
                overlay.replace_once(source, 'hook', 'new')

    def test_code_blocks_have_no_lost_lines(self):
        text = overlay.lang_fragment()
        text.encode('cp1251', errors='strict')
        for name in ['Ensure', 'Refresh', 'Menu', 'Capture', 'Restore']:
            for line in (overlay.SPEC / f'{name}.code').read_text().splitlines():
                self.assertIn('            0=' + line + '\n', text)

    def test_wrong_upstream_fails_before_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = next(iter(json.loads((overlay.SPEC / 'upstream.json').read_text())['files']))
            file = root / 'team' / first
            file.parent.mkdir(parents=True)
            file.write_text('unexpected upstream')
            output = root / 'output'
            with self.assertRaisesRegex(ValueError, 'Upstream changed'):
                overlay.prepare(root / 'team', output)
            self.assertFalse(output.exists())

    @unittest.skipUnless(os.environ.get('CE_TEAM_REFERENCE'), 'needs pinned team checkout')
    def test_real_upstream_integration(self):
        team = Path(os.environ['CE_TEAM_REFERENCE'])
        manifest = json.loads((overlay.SPEC / 'upstream.json').read_text())
        before = {rel: (team / rel).read_bytes() for rel in manifest['files']}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = overlay.prepare(team, root / 'result')
            second = overlay.prepare(team, root / 'second')
            self.assertEqual(report, second)
            self.assertFalse(report['game_tested'])
            tree = json.loads((root / 'result' / overlay.RSON).read_text())
            old = json.loads(before[overlay.RSON])
            # No graph rewrite, variable numbering changes, or replaced states.
            self.assertEqual(tree['Visual.Links'], old['Visual.Links'])
            self.assertEqual(tree['GraphPoint.Count'], old['GraphPoint.Count'])
            op = next(op for g in tree['Visual.Objects'] for op in g.get('Operations', [])
                      if op.get('Name') == 'Adapter smoke')
            for clear in ['ceClearStash();', 'ceClearStashR();']:
                index = next(i for i, line in enumerate(op['Code']) if line.strip() == clear)
                self.assertEqual(op['Code'][index-1].strip(), overlay.call('Restore'))
            transit = (root / 'result' / overlay.TRANSIT).read_text()
            self.assertLess(transit.index('CE.RaceOverlay.Capture'), transit.index('24=ceSaveStash();'))
            self.assertIn('ceStash(9+ceGoodsIdx,GoodsCount(Player(),ceGoodsIdx))', transit)
            self.assertEqual(report['stash_slots'], list(range(17, 23)))
            for rel, digest in report['files'].items():
                self.assertEqual(hashlib.sha256((root / 'result' / rel).read_bytes()).hexdigest(), digest)
            with self.assertRaisesRegex(ValueError, 'already exists'):
                overlay.prepare(team, root / 'result')
            with self.assertRaisesRegex(ValueError, 'separate'):
                overlay.prepare(team, team / 'dist' / 'overlay')
            # Failed publication must leave no partial output directory.
            with patch.object(Path, 'write_text', side_effect=OSError('disk full')):
                with self.assertRaises(OSError):
                    overlay.prepare(team, root / 'broken')
            self.assertFalse((root / 'broken').exists())
            self.assertEqual(list(root.glob('ce-race-*')), [])
        self.assertEqual(before, {rel: (team / rel).read_bytes() for rel in before})


if __name__ == '__main__':
    unittest.main()
