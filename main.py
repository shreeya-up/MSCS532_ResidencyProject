"""Interactive text-menu demo. Run: python main.py"""
from workout_tracker import StrengthTracker

USERS = ['U101', 'U102']
EXERCISES = ['BENCH', 'SQUAT', 'DEADLIFT']


def load_demo_data(tracker):
    tracker.add_workout('U101', 'W001', 'BENCH', '2026-11-04T10:00:00-05:00', [(50, 10), (60, 8)])
    tracker.add_workout('U101', 'W002', 'BENCH', '2026-11-06T10:00:00Z', [(60, 6)])
    # Backdated entry logged third: same 60 kg, so first logged PR remains W001.
    tracker.add_workout('U101', 'W003', 'BENCH', '2026-11-03T10:00:00Z', [(60, 5)])
    # Workout ID unique per USER, therefore U102 can also use W001.
    tracker.add_workout('U102', 'W001', 'SQUAT', '2026-11-05T12:00:00Z', [(80, 5)])


def show_workout(w):
    if w is None:
        print('No workout found')
        return
    print(f'User={w.user_id} | Workout={w.workout_id} | Exercise={w.exercise_id} | UTC={w.timestamp.isoformat()}')
    for i, s in enumerate(w.sets):
        print(f'  Set {i}: {s.weight_kg:g} kg x {s.repetitions} reps')


def main():
    tracker = StrengthTracker(USERS, EXERCISES)
    load_demo_data(tracker)
    print('Strength Training and Performance Tracking System')
    print('Preloaded users:', ', '.join(USERS))
    print('Exercises:', ', '.join(EXERCISES))
    while True:
        print('\n1 Add workout | 2 Get workout | 3 Date range | 4 Personal record | 5 Demo | 0 Exit')
        choice = input('Choose: ').strip()
        try:
            if choice == '1':
                user = input('User ID: ').strip()
                wid = input('Workout ID: ').strip()
                exercise = input('Exercise ID: ').strip()
                timestamp = input('ISO timestamp with timezone (e.g., 2026-11-07T12:00:00Z): ').strip()
                count = int(input('Number of sets: '))
                raw_sets = []
                for i in range(count):
                    weight = float(input(f'Set {i} weight (kg): '))
                    reps = int(input(f'Set {i} repetitions: '))
                    raw_sets.append((weight, reps))
                show_workout(tracker.add_workout(user, wid, exercise, timestamp, raw_sets))
            elif choice == '2':
                show_workout(tracker.get_workout(input('User ID: ').strip(), input('Workout ID: ').strip()))
            elif choice == '3':
                user = input('User ID: ').strip()
                start = input('Start ISO timestamp with timezone: ').strip()
                end = input('End ISO timestamp with timezone: ').strip()
                results = tracker.search_dates(user, start, end)
                print(f'{len(results)} result(s):')
                for w in results:
                    show_workout(w)
            elif choice == '4':
                user = input('User ID: ').strip()
                exercise = input('Exercise ID: ').strip()
                pr = tracker.get_personal_record(user, exercise)
                print('Personal record:', pr if pr else 'None yet')
            elif choice == '5':
                print('Demonstrating chronological order even with backdated entries:')
                for w in tracker.search_dates('U101', '2026-11-01T00:00:00Z', '2026-11-08T00:00:00Z'):
                    show_workout(w)
                print('U101 BENCH PR (first logged tie retained):', tracker.get_personal_record('U101', 'BENCH'))
                print('U102 isolated from U101:', tracker.get_workout('U102', 'W001'))
                print('Indexes valid:', tracker.validate_indexes())
            elif choice == '6':
                user = input('User ID: ').strip()
                exercise = input('Exercise ID: ').strip()
                k = int(input('How many (k): '))
                lifts = tracker.top_k_lifts(user, exercise, k)
                if not lifts:
                    print('No lifts logged yet')
                for rank, (wid, idx, kg, reps, ts) in enumerate(lifts, start=1):
                    print(f'  #{rank}: {kg:g} kg x {reps} reps | {wid} set {idx} | UTC {ts.isoformat()}')
            elif choice == '0':
                print('Goodbye')
                break
            else:
                print('Invalid option')
        except (ValueError, TypeError, KeyError, OverflowError) as exc:
            print('Error:', exc)
        except (EOFError, KeyboardInterrupt):
            print('\nExiting')
            break


if __name__ == '__main__':
    main()
