# Phase 2 Implementation Notes / Handoff to Phase 3

## Source

Implementation based on original Group 4 `Deliverable1_report.docx` (2026-11-06). It follows the documented function signatures, input rejection rules, UTC ordering, per-user isolation, and personal-record tie handling.

## Decisions

1. Preloaded demo IDs: users `U101`, `U102`; exercises `BENCH`, `SQUAT`, `DEADLIFT`. The original team's reply to GitHub Issue #1 allows sample IDs and requests backdated and tied PR examples.
2. Self-implemented AVL tree with LL/LR/RR/RL rotations. The original team's Issue #2 reply recommends self-implementation for code walkthroughs (subject to instructor's guidance).
3. Input sets are validated and copied into immutable `SetEntry` tuples, preventing later in-place alteration from invalidating cached PR values. Although the original brief calls this a dynamic array/list, this is a documented implementation-level variation; if strict list use is required, switch the stored tuple to a list while protecting it from external changes.
4. Workout IDs are unique within a user; sorting keys are `(aware UTC timestamp, workout ID)`.
5. Maximum PR weight is the key measure; repetitions do not break ties; ties preserve first successful insertion, including backdated timestamps.
6. Full tree and lookup consistency checks are available via `validate_indexes()` for testing.

## Assumptions and caveats

- Single-process, single-threaded operations; data in memory only.
- `add_workout()` validates before any index mutation, then inserts into AVL, dictionary, and PR cache. For unanticipated system-level failures, transactional rollback is not implemented; in-process recoverable partial failures can be handled by rebuilding user indexes from accepted workouts as specified by original brief.
- The use of `tuple` internally rather than Python list is the one minor deviation noted above.
- `sys.getsizeof()` only measures shallow object sizes; do not claim accurate total deep memory without a deep-object measurement.
- No measured throughput or memory claims are made here. Phase 3 should benchmark and profile with progressively larger datasets.

## Tested operations

Run `python -m unittest -v`. Coverage includes:
- User isolation and same workout ID across different users
- Duplicate workout rejection and validation of timestamps/weights/repetitions
- UTC conversion and invalid naive timestamps
- Inclusive date bounds, chronological ordering, and backdated insertion
- Equal-weight PR tie resolution with first logged set
- AVL balancing across insertion orders and comparison to sorted brute-force reference

## Next team

1. Clone the repository and run `python -m unittest -v`.
2. Run `python main.py`, enter option 5 to see a demo.
3. Profile `AVLTree.range_search`, `add_workout` and memory for larger datasets.
4. Verify the instructor's curveball requirements and apply optimizations without breaking tests.
5. Record before/after measurements, remaining limitations and decisions in Phase 3 notes.

