"""Tests for Phase 2 correctness and invariants. Run python -m unittest -v."""
import unittest
from datetime import datetime, timedelta, timezone
from workout_tracker import StrengthTracker
from avl_tree import AVLTree


class TrackerTests(unittest.TestCase):
    def setUp(self):
        self.t = StrengthTracker(['U1', 'U2'], ['BENCH', 'SQUAT'])
        self.time = '2026-11-07T10:00:00Z'

    def add(self, user='U1', wid='W1', exercise='BENCH', stamp=None, sets=None):
        return self.t.add_workout(user, wid, exercise, stamp or self.time, sets or [(60, 5)])

    def test_add_get_and_user_isolation(self):
        self.add()
        self.assertIsNone(self.t.get_workout('U2', 'W1'))
        self.add(user='U2')
        self.assertEqual(self.t.get_workout('U1', 'W1').user_id, 'U1')
        self.assertEqual(self.t.get_workout('U2', 'W1').user_id, 'U2')

    def test_duplicate_id_rejected_within_user(self):
        self.add()
        with self.assertRaises(ValueError): self.add()
        self.assertEqual(len(self.t.users['U1'].workouts), 1)

    def test_unknown_user_exercise(self):
        with self.assertRaises(ValueError): self.add(user='MISSING')
        with self.assertRaises(ValueError): self.add(exercise='MISSING')
        with self.assertRaises(ValueError): self.t.get_personal_record('U1', 'MISSING')

    def test_empty_and_invalid_sets(self):
        for sets in [[], [(0, 5)], [(-4, 5)], [(float('inf'), 5)],
                     [(float('nan'), 5)], [(50, 0)], [(50, 2.5)], [(50, True)], [(True, 5)]]:
            with self.subTest(sets=sets):
                with self.assertRaises(ValueError):
                    self.t.add_workout('U1', 'W1', 'BENCH', self.time, sets)
        self.assertEqual(self.t.users['U1'].workouts, {})

    def test_timezone_aware_and_naive_rejected(self):
        w = self.add(stamp='2026-11-07T05:00:00-05:00')
        self.assertEqual(w.timestamp.isoformat(), '2026-11-07T10:00:00+00:00')
        with self.assertRaises(ValueError): self.add(wid='W2', stamp='2026-11-07T10:00:00')
        with self.assertRaises(ValueError): self.add(wid='W3', stamp='not-a-date')

    def test_backdated_search_sorted_and_inclusive(self):
        self.add(wid='W3', stamp='2026-11-09T12:00:00Z')
        self.add(wid='W1', stamp='2026-11-07T12:00:00Z')
        self.add(wid='W2', stamp='2026-11-08T12:00:00Z')
        got = self.t.search_dates('U1', '2026-11-07T12:00:00Z', '2026-11-09T12:00:00Z')
        self.assertEqual([w.workout_id for w in got], ['W1', 'W2', 'W3'])
        self.assertTrue(self.t.validate_indexes())

    def test_same_timestamp_sorted_by_workout_id(self):
        self.add(wid='Z')
        self.add(wid='A')
        self.add(wid='M')
        got = self.t.search_dates('U1', self.time, self.time)
        self.assertEqual([w.workout_id for w in got], ['A', 'M', 'Z'])

    def test_empty_range_and_reversed_range(self):
        self.assertEqual(self.t.search_dates('U1', self.time, self.time), [])
        with self.assertRaises(ValueError):
            self.t.search_dates('U1', '2026-11-08T00:00:00Z', '2026-11-07T00:00:00Z')

    def test_pr_first_logged_wins_tie_even_backdated(self):
        self.add(wid='W1', stamp='2026-11-07T10:00:00Z', sets=[(60, 5), (60, 8)])
        self.add(wid='W2', stamp='2026-11-06T10:00:00Z', sets=[(60, 12)])
        pr = self.t.get_personal_record('U1', 'BENCH')
        self.assertEqual(pr[:4], ('W1', 0, 60.0, 5))
        self.add(wid='W3', sets=[(70, 2)])
        self.assertEqual(self.t.get_personal_record('U1', 'BENCH')[:4], ('W3', 0, 70.0, 2))

    def test_pr_none_and_per_user_per_exercise(self):
        self.assertIsNone(self.t.get_personal_record('U1', 'BENCH'))
        self.add(sets=[(60, 5)])
        self.add(user='U2', sets=[(100, 5)])
        self.assertEqual(self.t.get_personal_record('U1', 'BENCH')[2], 60)
        self.assertEqual(self.t.get_personal_record('U2', 'BENCH')[2], 100)
        self.assertIsNone(self.t.get_personal_record('U1', 'SQUAT'))

    def test_avl_stays_balanced_across_insertion_orders(self):
        for order in [range(150), reversed(range(150)), list(range(0, 150, 2)) + list(range(1, 150, 2))]:
            tree = AVLTree()
            base = datetime(2026, 1, 1, tzinfo=timezone.utc)
            for i in order:
                tree.insert((base + timedelta(seconds=i), str(i)), i)
            self.assertTrue(tree.validate_balance())
            self.assertEqual(len(tree.range_search(base, base + timedelta(seconds=149))), 150)

    def test_large_data_comparison_against_sort(self):
        for i in range(300):
            self.add(wid=f'W{i:04d}', stamp=f'2026-11-{1+i%20:02d}T12:00:00Z')
        results = self.t.search_dates('U1', '2026-11-05T00:00:00Z', '2026-11-15T23:59:59Z')
        expected = sorted((w for w in self.t.users['U1'].workouts.values()
                          if datetime(2026, 11, 5, tzinfo=timezone.utc) <= w.timestamp
                          <= datetime(2026, 11, 15, 23, 59, 59, tzinfo=timezone.utc)),
                          key=lambda w: (w.timestamp, w.workout_id))
        self.assertEqual(results, expected)
        self.assertTrue(self.t.validate_indexes())


if __name__ == '__main__':
    unittest.main()
