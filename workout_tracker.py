"""Multi-user in-memory strength-training tracker based on Group 4's Phase 1 brief.

Indexes per user:
- Python dictionary keyed by workout_id for expected O(1) exact retrieval.
- Custom AVL tree keyed by (UTC timestamp, workout_id) for ordered ranges.
- Dictionary keyed by exercise_id for expected O(1) PR retrieval.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
import math
from typing import Any
import heapq

_INF = math.inf

from avl_tree import AVLTree


@dataclass(frozen=True, slots=True)
class SetEntry:
    weight_kg: float
    repetitions: int


@dataclass(frozen=True, slots=True)
class Workout:
    user_id: str
    workout_id: str
    exercise_id: str
    timestamp: datetime
    sets: tuple[SetEntry, ...]


@dataclass(frozen=True, slots=True)
class PersonalRecord:
    workout_id: str
    set_index: int
    weight_kg: float
    repetitions: int
    timestamp: datetime

    def as_tuple(self):
        return (self.workout_id, self.set_index, self.weight_kg,
                self.repetitions, self.timestamp)


class _UserData:
    def __init__(self):
        self.workouts: dict[str, Workout] = {}
        self.by_date = AVLTree()
        self.pr_by_exercise: dict[str, PersonalRecord] = {}
        self.lift_heap: dict[str, list] = {}   # exercise_id -> min-heap
        self.log_seq = 0

class StrengthTracker:
    """In-memory prototype, no persistence, authentication, edit/delete, or concurrency."""

    def __init__(self, user_ids, exercise_ids):
        self.users = {uid: _UserData() for uid in user_ids}
        self.exercises = set(exercise_ids)
        if not self.users or not self.exercises:
            raise ValueError('Preload at least one user and one exercise')
        if any(not isinstance(uid, str) or not uid.strip() for uid in self.users):
            raise ValueError('User IDs must be nonempty strings')
        if any(not isinstance(eid, str) or not eid.strip() for eid in self.exercises):
            raise ValueError('Exercise IDs must be nonempty strings')

    def _user(self, user_id):
        if user_id not in self.users:
            raise ValueError(f'Unknown user: {user_id}')
        return self.users[user_id]

    @staticmethod
    def _utc(value):
        """Require aware datetime or ISO-8601 text, return UTC datetime."""
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError as exc:
                raise ValueError('Invalid ISO-8601 timestamp') from exc
        if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
            raise ValueError('Timestamp must be timezone-aware')
        try:
            return value.astimezone(timezone.utc)
        except (OverflowError, ValueError) as exc:
            raise ValueError('Invalid timestamp') from exc

    @staticmethod
    def _check_set_slow(index, weight, reps):
        """Original (general) checks, used only for unusual input types."""
        if (isinstance(weight, bool) or not isinstance(weight, (int, float))
                or not math.isfinite(weight) or weight <= 0):
            raise ValueError(f'Weight at set {index} must be finite and > 0')
        if isinstance(reps, bool) or not isinstance(reps, int) or reps <= 0:
            raise ValueError(f'Repetitions at set {index} must be a positive integer')
        return float(weight), reps

    @classmethod
    def _sets(cls, raw_sets):
        """Validate sets; return a tuple of SetEntry. O(s).

        Phase 3: fast path for the common input (a tuple/list pair with a plain
        float/int weight and a plain int rep count): exact type checks and one
        chained comparison instead of ~8 isinstance/isfinite calls per set.
        Anything else goes through the original checks, so accepted and
        rejected inputs are exactly the same as before.
        """
        if not isinstance(raw_sets, (list, tuple)) or not raw_sets:
            raise ValueError('At least one set is required')
        output = []
        for index, item in enumerate(raw_sets):
            item_type = type(item)
            if item_type is tuple or item_type is list:
                if len(item) != 2:
                    raise ValueError(f'Invalid set at index {index}')
                weight, reps = item
            elif item_type is SetEntry:
                weight, reps = item.weight_kg, item.repetitions
            elif isinstance(item, dict):
                try:
                    weight = item['weight_kg']
                    reps = item['repetitions']
                except KeyError as exc:
                    raise ValueError('Each set needs weight_kg and repetitions') from exc
            elif isinstance(item, (tuple, list)) and len(item) == 2:
                weight, reps = item
            else:
                raise ValueError(f'Invalid set at index {index}')
            weight_type = type(weight)
            if (weight_type is float or weight_type is int) and type(reps) is int:
                # 0 < w < inf is False for 0, negatives, inf and NaN.
                if not 0 < weight < _INF:
                    raise ValueError(f'Weight at set {index} must be finite and > 0')
                if reps <= 0:
                    raise ValueError(f'Repetitions at set {index} must be a positive integer')
                output.append(SetEntry(float(weight), reps))
            else:
                output.append(SetEntry(*cls._check_set_slow(index, weight, reps)))
        return tuple(output)

    def add_workout(self, user_id, workout_id, exercise_id, timestamp, sets):
        """Validate and add a workout; return Workout.

        Workout ID unique per user. All indexes updated on success. Expected
        amortized O(s + log(n+1)) with s sets and n user's existing workouts.
        """
        user = self._user(user_id)
        if not isinstance(workout_id, str) or not workout_id.strip():
            raise ValueError('Workout ID must be a nonempty string')
        if workout_id in user.workouts:
            raise ValueError(f'Duplicate workout ID for user {user_id}: {workout_id}')
        if exercise_id not in self.exercises:
            raise ValueError(f'Unknown exercise: {exercise_id}')
        utc_time = self._utc(timestamp)
        validated_sets = self._sets(sets)
        workout = Workout(user_id, workout_id, exercise_id, utc_time, validated_sets)
        # Insert AVL index first, since that is the only operation that could
        # fail within normal single-process execution after validation.
        user.by_date.insert((utc_time, workout_id), workout)
        user.workouts[workout_id] = workout
        seq = user.log_seq
        user.log_seq += 1
        heap = user.lift_heap.setdefault(exercise_id, [])
        push = heapq.heappush
        # Phase 3: one pass over the sets does both jobs. The heap stores a plain
        # tuple (already in get_personal_record's shape) instead of building a
        # PersonalRecord object per set, and the PR is built once, at the end.
        old_pr = user.pr_by_exercise.get(exercise_id)
        best_weight = old_pr.weight_kg if old_pr is not None else -1.0
        best_index = -1
        for i, entry in enumerate(validated_sets):
            weight = entry.weight_kg
            push(heap, (-weight, seq, i,
                        (workout_id, i, weight, entry.repetitions, utc_time)))
            # Strictly greater only, so an equal-weight PR keeps first logged set.
            if weight > best_weight:
                best_weight, best_index = weight, i
        if best_index >= 0:
            user.pr_by_exercise[exercise_id] = PersonalRecord(
                workout_id, best_index, best_weight,
                validated_sets[best_index].repetitions, utc_time)
        return workout

    def get_workout(self, user_id, workout_id):
        """Return a user's workout or None; expected O(1)."""
        return self._user(user_id).workouts.get(workout_id)

    def search_dates(self, user_id, start_utc, end_utc):
        """Return matching workouts sorted by date/ID; bounds inclusive.

        Worst-case O(log(n+1) + k) for AVL search of k matches.
        """
        user = self._user(user_id)
        start, end = self._utc(start_utc), self._utc(end_utc)
        if start > end:
            raise ValueError('Start date cannot be after end date')
        return user.by_date.range_search(start, end)

    def get_personal_record(self, user_id, exercise_id):
        """Return PR (workout ID, 0-based set index, weight, reps, UTC timestamp), or None."""
        user = self._user(user_id)
        if exercise_id not in self.exercises:
            raise ValueError(f'Unknown exercise: {exercise_id}')
        record = user.pr_by_exercise.get(exercise_id)
        return record.as_tuple() if record else None

    def validate_indexes(self):
        """Development helper: confirm per-user AVL and lookup indexes agree."""
        for user in self.users.values():
            user.by_date.validate_balance()
            all_workouts = user.by_date.range_search(datetime.min.replace(tzinfo=timezone.utc),
                                                       datetime.max.replace(tzinfo=timezone.utc))
            assert len(all_workouts) == len(user.workouts)
            assert {w.workout_id for w in all_workouts} == set(user.workouts)
        return True

    def top_k_lifts(self, user_id, exercise_id, k):
        user = self._user(user_id)
        if exercise_id not in self.exercises:
            raise ValueError(f'Unknown exercise: {exercise_id}')
        if isinstance(k, bool) or not isinstance(k, int) or k < 0:
            raise ValueError('k must be a non-negative integer')
        heap = user.lift_heap.get(exercise_id, [])
        result = []
        if k == 0 or not heap:
            return result
        frontier = [(heap[0], 0)]                  # (entry, index in main heap)
        while frontier and len(result) < k:
            entry, i = heapq.heappop(frontier)
            result.append(entry[3])                # stored in get_personal_record's tuple shape
            for c in (2 * i + 1, 2 * i + 2):
                if c < len(heap):
                    heapq.heappush(frontier, (heap[c], c))
        return result
