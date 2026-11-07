# Strength Training and Performance Tracking System
## Phase 2 — Manual QA Test Cases and Execution Steps

**Course:** MSCS 532 — Algorithms and Data Structures  
**Project:** Strength Training and Performance Tracking System  
**Scope:** Local browser proof of concept (`web_app.py` + `index.html`) and Python tracker  
**Execution environment:** Windows, Python 3.14, Microsoft Edge, `http://127.0.0.1:8000`  
**Test evidence:** Browser walkthrough screenshots and a prior run of `py -m unittest -v` reporting 12 tests passed.  
**Status convention:** **Observed pass** = manually demonstrated in the browser during Phase 2; **Not executed** = planned, not yet verified; **Automated pass** = previously reported passing in Python unittest. These are not interchangeable.

### Preconditions and test data

1. Open the project directory `Strength_Tracker_Phase2_Python` in VS Code.
2. In a terminal, run `py web_app.py`. Keep the server running.
3. Open `http://127.0.0.1:8000` in Edge or Chrome.
4. A fresh server session loads two users (`U101`, `U102`) and four sample workouts. The sample exercise IDs include `BENCH`, `SQUAT`, and `DEADLIFT`.
5. The application stores data **in memory**. Stopping the server with `Ctrl+C` and starting it again resets the sample data. Use a fresh server session to repeat test cases that depend on the initial count or workout IDs.
6. Where a test calls for a new workout, use a workout ID that does not already exist for the selected user, unless the test specifically checks duplicates. The UI adds **one set** per submission; the backend supports multiple sets.

### A. Manual browser functional tests

| ID | Test case | Detailed test steps | Expected result | Execution status / evidence |
|---|---|---|---|---|
| TC-01 | Load dashboard and verify initial data | 1. Start a fresh server. 2. Open the application URL. 3. Click **Dashboard**. | Dashboard shows **2 preloaded users**, **4 total workouts**, **Data Indexes: Valid**. | **Observed pass** — initial dashboard screenshot. |
| TC-02 | Add a valid workout | 1. Click **Add workout**. 2. Select user `U101`. 3. Enter workout ID `W004`. 4. Select `BENCH`. 5. Enter timestamp `2026-11-07T12:00:00Z`. 6. Enter weight `85` kg and repetitions `10`. 7. Click **Save workout**. | Confirmation says workout `W004` was saved successfully. | **Observed pass** — success message screenshot. |
| TC-03 | Retrieve workout by user and ID | 1. Click **Search workout**. 2. Select `U101`. 3. Enter `W004`. 4. Click **Find workout**. | Returned workout shows `U101`, `W004`, `BENCH`, UTC timestamp, and **85 kg × 10 reps**. | **Observed pass** — lookup result screenshot. |
| TC-04 | Search workouts by UTC date interval | 1. Click **Date-range search**. 2. Select `U101`. 3. Enter start `2026-11-01T00:00:00Z`. 4. Enter end `2026-11-08T23:59:59Z`. 5. Click **Search date range**. | **4 matching workouts**, sorted by UTC timestamp: `W003` (Nov 3), `W001` (Nov 4), `W002` (Nov 6), `W004` (Nov 7). | **Observed pass** — matching count and ordered results screenshots. |
| TC-05 | View updated personal record | 1. Click **Personal record**. 2. Select user `U101`. 3. Select exercise `BENCH`. 4. Click **Find personal record**. | Highest set is **85 kg**, **10 repetitions**, workout `W004`, set index `0`. | **Observed pass** — personal record screenshot. |
| TC-06 | Confirm dashboard count and index health after insertion | 1. After TC-02, return to **Dashboard**. 2. Review counters and workout table. | **5 total workouts**, **2 preloaded users**, **Data Indexes: Valid**, and new `W004` shown in dashboard. | **Observed pass** — updated dashboard screenshot. |
| TC-07 | Reject duplicate workout ID within same user | 1. With `U101/W004` already present, open **Add workout**. 2. Enter the same user and workout ID with otherwise valid values. 3. Save. | Validation error; duplicate is not inserted; workout count does not increase. | **Not executed manually**. |
| TC-08 | Permit same workout ID for different users | 1. Keep `U101/W004` in place. 2. Add an otherwise valid workout with `U102/W004`. 3. Search by user and ID separately. | Both user-scoped workouts can exist independently; searches return the proper user's record. | **Not executed manually**. |
| TC-09 | Reject zero weight | 1. Add a new workout with valid user, ID, exercise, timestamp, and repetitions. 2. Set weight to `0`. 3. Save. | Workout is rejected; no new workout is stored. | **Not executed manually**. |
| TC-10 | Reject negative weight | 1. Enter a new valid workout. 2. Set weight to `-10`. 3. Save. | Workout is rejected; no new workout is stored. | **Not executed manually**. |
| TC-11 | Accept positive finite weight without arbitrary fixed cap | 1. Add a new workout with weight `10000` kg and valid remaining fields. 2. Save. 3. Retrieve it. | Positive finite value accepted according to current validation rules; retrieved value matches. This is a validation test, not a realistic-lifting claim. | **Not executed manually**. |
| TC-12 | Reject zero or negative repetitions | 1. Enter a new valid workout with repetitions `0`; attempt save. 2. Repeat with `-5` for another new ID. | Both invalid inputs are rejected; records are not added. | **Not executed manually**. |
| TC-13 | Search for unknown workout ID | 1. Click **Search workout**. 2. Choose `U101`. 3. Enter an unused ID such as `W999`. 4. Click **Find workout**. | Clear not-found or error response; no unrelated record returned. | **Not executed manually**. |
| TC-14 | Reject reversed date range | 1. Open **Date-range search**. 2. Set start to `2026-11-08T00:00:00Z`. 3. Set end to `2026-11-01T00:00:00Z`. 4. Search. | Invalid interval rejected; no misleading search results. | **Not executed manually**. |
| TC-15 | Verify inclusive date boundaries | 1. Locate a known workout timestamp. 2. Set both start and end to that exact UTC timestamp for its user. 3. Search. | Workout at the boundary is included. Other workouts with the same timestamp, if any, are ordered by workout ID. | **Not executed manually**. |
| TC-16 | Preserve earliest logged lift when PR weight ties | 1. Note the current `U101/BENCH` personal record. 2. Add a later-logged workout with the same maximum weight (`85` kg) and a different workout ID. 3. Find personal record again. | Original first-logged maximum-weight set remains the personal record, even if the new workout has an earlier timestamp. | **Not executed manually**. |
| TC-17 | Verify user isolation in results | 1. Search workout `W001` for `U101`. 2. Search workout `W001` for `U102`. 3. Compare returned exercises/sets. | Each lookup uses the selected user's data. One user's records are not returned for the other. | **Not executed manually**. |
| TC-18 | Restart resets in-memory data | 1. Confirm there are 5 workouts after TC-02. 2. Return to VS Code and press `Ctrl+C` in the server terminal. 3. Restart with `py web_app.py`. 4. Refresh Dashboard. | Dashboard returns to its original **4 sample workouts**; newly added `W004` for `U101` is no longer present. | **Not executed manually**; expected behavior documented by app. |
| TC-19 | Confirm current browser has no user-registration feature | 1. Inspect the left navigation and available forms. 2. Look for a user creation form. | No browser **Add User** option; app uses preloaded users. This is a documented current scope limitation, not a failure. | **Observed** in supplied browser screenshots. |
| TC-20 | Check multi-set backend support | 1. Run or inspect a backend test involving two or more sets for a single workout. 2. Retrieve that workout. | All sets remain associated with one workout; browser Add Workout form itself accepts one set per submission. | **Not executed manually**; supported by sample `W001` with 2 sets and backend implementation. |

### B. Automated unit-test execution

| ID | Test | Steps | Expected result | Status |
|---|---|---|---|---|
| AT-01 | Python unit-test suite | 1. In VS Code, open a terminal in `Strength_Tracker_Phase2_Python`. 2. Run `py -m unittest -v`. 3. Check the process summary and all individual test cases. | All 12 unit tests report `ok`; summary reports `Ran 12 tests` and `OK`. | **Automated pass** — previously executed locally (12 tests passed). |

### C. Future capacity/performance tests — not yet executed

| ID | Scenario | Proposed steps | Measurement / expected outcome | Status |
|---|---|---|---|---|
| PERF-01 | 1,000 workout records | Generate 1,000 valid workouts through the Python backend, then time insertion and sample range searches. | Record elapsed time, record count, index validity, and peak memory; no unverified threshold stated. | **Not executed** |
| PERF-02 | 10,000 workout records | Generate 10,000 valid backend workouts, then measure insert, lookup, date-range search, and process memory. | Record measured timings and bytes/record; review any practical capacity limit. | **Not executed** |
| PERF-03 | Variable-length sets | Compare memory usage for workouts containing 1, 10, and 100 valid sets via backend calls. | Measure added memory per workout and document potential need for a configurable set limit. | **Not executed** |

### Known design constraints and handoff notes

- User registration is outside the present browser UI; there are **two predefined users**. The design does not specify a maximum total user count.
- There is **no enforced fixed maximum** for workout count or for number of sets in the backend. A future team should evaluate limits and memory growth.
- Weights must be **positive, finite numbers**; repetitions must be **positive integers**. Unknown users/exercises, duplicates within the same user, and invalid time inputs must be rejected.
- Keys for AVL date ordering use the **UTC timestamp and workout ID**; the workout data is maintained in Python structures. AVL insertion is `O(log n)`, date-range reporting `O(log n + k)`, and dictionary lookup is `O(1)` on average.
- Storage is in memory. Overall storage grows with the number of workouts and stored sets, approximately `O(n + s)`; this is a **space**, not time, complexity expression.
- Actual memory consumption **in bytes per record** and performance for 10,000 records have **not been measured**; do not claim benchmark results or an enforced 10,000-record capacity.
- **Observed pass** entries document the completed browser demonstration only. The remaining scenarios are proposed steps for future execution and are not claims of successful testing.

### How to rerun the application

```powershell
cd Strength_Tracker_Phase2_Python
py web_app.py
```

Open `http://127.0.0.1:8000` in a browser. To stop the server, press `Ctrl+C` in the terminal.

### How to rerun automated tests

```powershell
py -m unittest -v
```

**Submission note:** Commit this file as `TEST_CASES.md` alongside `test_workout_tracker.py`, implementation files, README, implementation notes, and any required AI Usage Appendix. Preserve the inherited Phase 1 report and license.
