
"""Phase 3 tests for top_k_lifts. Run: python -m unittest -v"""
import random
import unittest
from workout_tracker import StrengthTracker
 
 
class TopKTests(unittest.TestCase):
    def setUp(self):
        self.t = StrengthTracker(['U1', 'U2'], ['BENCH', 'SQUAT'])
 
    def add(self, wid, sets, stamp='2026-11-07T10:00:00Z', user='U1', ex='BENCH'):
        self.t.add_workout(user, wid, ex, stamp, sets)
 
    def ids(self, k, user='U1', ex='BENCH'):
        return [(r[0], r[1]) for r in self.t.top_k_lifts(user, ex, k)]
 
    def test_empty_and_zero(self):
        self.assertEqual(self.t.top_k_lifts('U1', 'BENCH', 5), [])
        self.add('W1', [(60, 5)])
        self.assertEqual(self.t.top_k_lifts('U1', 'BENCH', 0), [])
 
    def test_bad_arguments(self):
        for bad in [-1, 2.0, True, None, '3']:
            with self.subTest(k=bad), self.assertRaises(ValueError):
                self.t.top_k_lifts('U1', 'BENCH', bad)
        with self.assertRaises(ValueError): self.t.top_k_lifts('NOPE', 'BENCH', 1)
        with self.assertRaises(ValueError): self.t.top_k_lifts('U1', 'NOPE', 1)
 
    def test_descending_and_k_larger_than_n(self):
        self.add('W1', [(60, 5), (80, 3), (70, 4)])
        self.assertEqual(self.ids(10), [('W1', 1), ('W1', 2), ('W1', 0)])
 
    def test_ties_earliest_logged_even_when_backdated(self):
        self.add('W1', [(100, 1)], stamp='2026-11-07T10:00:00Z')
        self.add('W2', [(100, 1), (100, 2)], stamp='2026-11-01T10:00:00Z')  # backdated, logged later
        self.add('W3', [(100, 1)], stamp='2026-11-03T10:00:00Z')
        self.assertEqual(self.ids(4), [('W1', 0), ('W2', 0), ('W2', 1), ('W3', 0)])
 
    def test_k1_matches_personal_record(self):
        self.add('W1', [(60, 5), (60, 8)])
        self.add('W2', [(60, 12)], stamp='2026-11-06T10:00:00Z')
        self.assertEqual(self.t.top_k_lifts('U1', 'BENCH', 1)[0],
                         self.t.get_personal_record('U1', 'BENCH'))
 
    def test_isolation_by_user_and_exercise(self):
        self.add('W1', [(60, 5)])
        self.add('W1', [(200, 1)], user='U2')
        self.add('W2', [(150, 1)], ex='SQUAT')
        self.assertEqual(self.ids(5), [('W1', 0)])
 
 
 
if __name__ == '__main__':
    unittest.main()
