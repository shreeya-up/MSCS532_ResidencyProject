# Strength Training and Performance Tracking System — Phase 2 POC

Inherited project: `https://github.com/shreeya-up/Strength_Tracker-Group_4`

## Start quickly

Requires Python 3.10+; standard library only.

```bash
python main.py
```

Choose **5** for the automatic demonstration, or choose 1–4 to use the operations interactively.

Run tests:

```bash
python -m unittest -v
```

## Implemented operations

- `add_workout(user_id, workout_id, exercise_id, timestamp, sets)` validates data and adds a workout.
- `get_workout(user_id, workout_id)` fetches by per-user ID or returns `None`.
- `search_dates(user_id, start_utc, end_utc)` returns sorted workouts, boundaries inclusive.
- `get_personal_record(user_id, exercise_id)` returns `(workout_id, zero_based_set_index, weight_kg, repetitions, utc_timestamp)` or `None`.

### Data structures

- `dict` by user ID, then workout ID: expected O(1) exact lookup.
- Custom AVL tree indexed by `(UTC timestamp, workout ID)`: O(log n) insert, O(log n + k) range query.
- `tuple` of `SetEntry` elements for individual workout sets; the input interface accepts Python lists (the brief specifies a dynamic array/list for sets). To match the brief literally, a plain `list` could be used instead. The implementation stores a *tuple snapshot* to avoid accidental mutations after indexing; sequential scanning remains O(s).
- Per-user, per-exercise dictionary caches PR: expected O(1) retrieval; ties keep the first logged set.

## Preloaded demo data

Users: `U101`, `U102`. Exercises: `BENCH`, `SQUAT`, `DEADLIFT`.

- U101: W001 and W002 with 60 kg bench PR tie; W003 is **backdated** and ties at 60 kg.
- U102: W001 squat, demonstrating that workout IDs are unique *per user*.

Original team's GitHub Issue #1 confirms we may choose sample IDs and must demonstrate multiple users, backdated workouts, and equal-weight PRs. See Issue #2 for AVL recommendation.

## Explicit limits

Prototype only: no authentication, edits, deletions, database, persistence, concurrency, endurance metrics, or crash recovery. `Real-time` means in-process updates after a call returns, not real-time distributed consistency.

Important: This is a proposed Phase 2 implementation, **not an original Phase 1 artifact**. The Phase 2 group must review and understand code, run tests, make its own commits to the assigned repo, and follow instructor instructions. Do not move the Phase 1 tag.

## Browser interface (local-only demo)

Run `py web_app.py` from this folder, then visit **http://127.0.0.1:8000** in Chrome or Edge. This browser UI uses the exact same Python `StrengthTracker` and AVL tree as the CLI. No pip installation is required. The browser form adds one set at a time, while the backend supports multi-set workouts. User IDs and exercises are preloaded. All data is memory-only and resets when restarting the server. Press Ctrl+C in the terminal to stop the server.
## Phase 2 — Team Members

1. Bharath Origanti
2. Harika Rajisetty
3. Amar Kulkarni
4. Chandra Kiran Billingi
5. Fahad Jafar Mohammed

**Course: MSCS 532 — Algorithms and Data Structures
Phase: 2 — Implementation**
