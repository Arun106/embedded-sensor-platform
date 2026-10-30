import copy
import json
import unittest
from pathlib import Path
from board import flash, plan

ROOT = Path(__file__).resolve().parents[1]


class UpgradeTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((ROOT / 'config/release.json').read_text())
        self.state = json.loads((ROOT / 'config/board.json').read_text())

    def test_bridge_then_target_and_rerun(self):
        self.assertEqual(plan(self.config, self.state), ['2', '3'])
        bridge = flash(self.config, self.state, '2')
        final = flash(self.config, bridge, '3')
        self.assertEqual(final['history'], ['2', '3'])
        self.assertEqual(plan(self.config, final), [])

    def test_direct_from_bridge(self):
        self.state['firmware'] = '2'
        self.assertEqual(plan(self.config, self.state), ['3'])

    def test_cannot_skip_bridge_and_no_mutation(self):
        original = copy.deepcopy(self.state)
        with self.assertRaises(ValueError):
            flash(self.config, self.state, '3')
        self.assertEqual(original, self.state)

    def test_incompatible_or_unknown_state(self):
        for key, value in [('board_revision', 'B'), ('bootloader', '0'), ('firmware', 'unknown'), ('simulation', False)]:
            state = dict(self.state, **{key: value})
            with self.subTest(key=key), self.assertRaises(ValueError):
                plan(self.config, state)

    def test_invalid_release_path(self):
        self.config['upgrade_paths']['1'] = ['2']
        with self.assertRaises(ValueError):
            plan(self.config, self.state)


if __name__ == '__main__':
    unittest.main()
