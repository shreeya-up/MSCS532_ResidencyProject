"""Profile the core StrengthTracker operations at scale (no UI / web layer).

Usage: python profile_core.py [n]      (default n = 100000 workouts)
Writes profile_core.out (open with snakeviz or pstats) and prints the hot spots.

All random data is generated BEFORE profiling starts, so the profile shows
only StrengthTracker's own code, not the random-number generator.
"""
import cProfile
import pstats
import random
import sys
from datetime import datetime, timedelta, timezone

from workout_tracker import StrengthTracker

N = int(sys.argv[1]) if len(sys.argv) > 1 else 100_000
USERS = ['U101', 'U102']
EXERCISES = ['BENCH', 'SQUAT', 'DEADLIFT']
BASE = datetime(2024, 1, 1, tzinfo=timezone.utc)


def make_data():
    """Same seeded data every run, so before/after profiles are comparable."""
    rng = random.Random(2026)
    workouts = []
    for i in range(N):
        stamp = (BASE + timedelta(seconds=rng.randrange(2 * 365 * 86400))).isoformat()
        sets = [(rng.randint(8, 100) * 2.5, rng.randint(1, 12)) for _ in range(rng.randint(1, 4))]
        workouts.append((rng.choice(USERS), f'W{i}', rng.choice(EXERCISES), stamp, sets))
    lookups = [(rng.choice(USERS), f'W{rng.randrange(N)}') for _ in range(5_000)]
    ranges = []
    for _ in range(500):
        start = BASE + timedelta(days=rng.randrange(700))
        ranges.append((rng.choice(USERS), start, start + timedelta(days=7)))
    queries = [(rng.choice(USERS), rng.choice(EXERCISES)) for _ in range(5_000)]
    return workouts, lookups, ranges, queries


def workload(workouts, lookups, ranges, queries):
    t = StrengthTracker(USERS, EXERCISES)
    for w in workouts:                      # 1. Inserts (ISO strings, as the CLI sends them)
        t.add_workout(*w)
    for user, wid in lookups:               # 2. Exact lookups
        t.get_workout(user, wid)
    for user, start, end in ranges:         # 3. Date-range searches (~1 week)
        t.search_dates(user, start, end)
    for user, exercise in queries:          # 4. PR and top-k (curveball)
        t.get_personal_record(user, exercise)
        t.top_k_lifts(user, exercise, 10)


if __name__ == '__main__':
    data = make_data()                      # not profiled
    profiler = cProfile.Profile()
    profiler.enable()
    workload(*data)
    profiler.disable()
    profiler.dump_stats('profile_core.out')
    stats = pstats.Stats(profiler).strip_dirs()
    print('=== Top 20 by cumulative time (which operations are slow) ===')
    stats.sort_stats('cumulative').print_stats(20)
    print('=== Top 15 by own time (where the CPU actually goes) ===')
    stats.sort_stats('tottime').print_stats(15)