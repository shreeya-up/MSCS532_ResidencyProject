"""Local-only browser UI for the Strength Tracker proof of concept.

Run: py web_app.py
Open: http://127.0.0.1:8000

Standard library only. State is in memory and resets when this server restarts.
"""
from dataclasses import asdict
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from urllib.parse import urlsplit
from workout_tracker import StrengthTracker
from main import USERS, EXERCISES, load_demo_data

HOST, PORT = '127.0.0.1', 8000
tracker = StrengthTracker(USERS, EXERCISES)
load_demo_data(tracker)


def workout_json(workout):
    if workout is None:
        return None
    return {
        'user_id': workout.user_id, 'workout_id': workout.workout_id,
        'exercise_id': workout.exercise_id, 'timestamp': workout.timestamp.isoformat(),
        'sets': [asdict(entry) for entry in workout.sets],
    }


def handle_action(action, data):
    if action == 'add':
        result = tracker.add_workout(data['user_id'], data['workout_id'],
                                     data['exercise_id'], data['timestamp'], data['sets'])
        return {'workout': workout_json(result), 'message': 'Workout saved successfully.'}
    if action == 'get':
        return {'workout': workout_json(tracker.get_workout(data['user_id'], data['workout_id']))}
    if action == 'dates':
        return {'workouts': [workout_json(w) for w in tracker.search_dates(data['user_id'], data['start'], data['end'])]}
    if action == 'pr':
        pr = tracker.get_personal_record(data['user_id'], data['exercise_id'])
        return {'record': None if pr is None else {
            'workout_id': pr[0], 'set_index': pr[1], 'weight_kg': pr[2],
            'repetitions': pr[3], 'timestamp': pr[4].isoformat()}}
    if action == 'overview':
        return {'users': USERS, 'exercises': EXERCISES,
                'workout_count': sum(len(user.workouts) for user in tracker.users.values()),
                'workouts': [workout_json(w) for uid in USERS for w in tracker.users[uid].by_date.range_search(
                    datetime.min.replace(tzinfo=__import__('datetime').timezone.utc),
                    datetime.max.replace(tzinfo=__import__('datetime').timezone.utc))],
                'indexes_valid': tracker.validate_indexes()}
    if action == 'topk':
        lifts = tracker.top_k_lifts(data['user_id'], data['exercise_id'], int(data['k']))
        return {'lifts': [{'rank': rank, 'workout_id': r[0], 'set_index': r[1],
                        'weight_kg': r[2], 'repetitions': r[3],
                        'timestamp': r[4].isoformat()}
                        for rank, r in enumerate(lifts, start=1)]}
    raise ValueError('Unknown action')

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if urlsplit(self.path).path != '/':
            self.send_error(404)
            return
        payload = (Path(__file__).with_name('index.html')).read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_POST(self):
        if urlsplit(self.path).path != '/api':
            self.send_error(404)
            return
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if length <= 0 or length > 100_000:
                raise ValueError('Invalid request size')
            body = json.loads(self.rfile.read(length))
            if not isinstance(body, dict):
                raise ValueError('Request must be an object')
            result = handle_action(body.get('action'), body)
            status = 200
            response = {'ok': True, **result}
        except (ValueError, KeyError, TypeError, OverflowError) as exc:
            status = 400
            response = {'ok': False, 'error': str(exc)}
        payload = json.dumps(response, allow_nan=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(payload)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, fmt, *args):
        return


if __name__ == '__main__':
    print(f'Strength Tracker browser UI running at http://{HOST}:{PORT}')
    print('Press Ctrl+C to stop. Data will reset when server restarts.')
    try:
        ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
    except KeyboardInterrupt:
        print('\nServer stopped.')
