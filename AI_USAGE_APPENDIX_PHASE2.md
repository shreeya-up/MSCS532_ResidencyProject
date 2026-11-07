# Phase 2 — AI Usage Appendix

**Project:** Strength Training and Performance Tracking System  
**Course:** MSCS 532 — Algorithms and Data Structures  
**Deliverable:** Phase 2 Implementation / Proof of Concept  
**Repository:** https://github.com/shreeya-up/Strength_Tracker-Group_4  
**Date:** November 7, 2026

## 1. Purpose and disclosure

The Phase 2 team used ChatGPT as an AI-assisted development and documentation resource while implementing the workout tracker inherited from the Phase 1 design team. AI assistance contributed to drafting and explaining Python implementation code, a local browser demonstration, unit-test examples, README/implementation notes, and QA test cases. The team was responsible for reviewing the inherited requirements, running the application, checking outputs, and deciding what to submit. This appendix documents representative **paraphrases of the significant requests** made to the assistant; they are not presented as verbatim transcripts.

## 2. Significant AI requests and how the output was used

| Area | Representative request / question (paraphrased) | AI contribution | Team verification / decision |
|---|---|---|---|
| Inherited design | Help implement the Phase 1 Strength Tracker specification, including user-scoped workouts, workout sets, UTC timestamps, validation, date search, and personal records. | Drafted a modular Python proof of concept. | Team ran the Python application locally in VS Code and reviewed its main user-visible operations. |
| Data structures | Implement an AVL tree for chronologically ordered workouts and dictionaries for direct lookup and personal-record caching. | Drafted AVL-tree and workout-tracking modules and described expected complexity. | Team demonstrated chronological date-range results and successful workout-ID lookup. Formal large-scale benchmarking was not performed. |
| Automated tests | Prepare tests for valid and invalid workouts, duplicate IDs, dates, and personal records. | Drafted `test_workout_tracker.py` with 12 automated tests. | Team ran `py -m unittest -v` on Windows; the observed result was **12 tests run, OK**. |
| Local demonstration | Provide commands to run and explain the Python application for a professor walkthrough. | Suggested `py main.py`, demonstration menu actions, and explanations of the functions. | Team ran the CLI and displayed its demo output. |
| Browser interface | Make the working Python project open locally in a web browser rather than only in the terminal. | Drafted a local Python web server (`web_app.py`) and browser UI (`index.html`). | Team launched `py web_app.py` and visited `http://127.0.0.1:8000` in Microsoft Edge. |
| Browser workflow testing | Provide example entries and expected results for add, search, date-range search, and personal-record functions. | Suggested an example workout and guided the manual demonstration. | Team saved `U101 / W004 / BENCH / 85 kg / 10 reps`, retrieved W004, obtained four workouts in the November 1–8 range, saw the 85 kg personal record, and observed the dashboard increase to five workouts with valid indexes. |
| QA documentation | Produce step-by-step manual test cases for the Phase 2 repository. | Drafted `TEST_CASES.md` and differentiated completed manual checks from planned tests. | The document was committed to GitHub; planned scenarios must not be reported as completed tests without execution evidence. |
| Walkthrough and handoff | Explain AVL-tree keys, complexity, record size, in-memory capacity, limitations, and what Phase 3 could optimize. | Helped formulate technical explanations and handoff recommendations. | Team discussed these topics with the professor. Exact bytes per workout and workload limits remained unmeasured. |

## 3. AI limitations, corrections, and independent checking

AI-generated material required review rather than automatic acceptance. During the walkthrough, the team identified that **O(n + s)** describes the overall retained-data **space** requirement (n workouts and s sets), not the time complexity of all operations. The AVL tree uses **O(n)** node space and has **O(log n)** height; date-range reporting is expected to take **O(log n + k)** for k matching entries under the designed indexing approach. The professor also asked for the **actual bytes per workout record**, which the team had **not measured**. A compact fixed-field example is not equivalent to the memory used by Python dictionaries, strings, tuples, lists, and object references, so no measured record size or 10,000-record capacity is claimed. The team also confirmed that the browser form currently adds **one set per submission**, even though the backend is designed to support multiple sets, and that user registration, persistence, and unbounded-memory controls are not implemented in this proof of concept.

The team checked AI-assisted output by running the Python unit tests and using the browser to perform a concrete add-and-retrieve workflow. The **12 automated tests passed** in the observed local run, and the named browser actions produced the expected results. These checks are evidence for the specific tested scenarios, **not** proof of production readiness, security, scalability, or every planned manual test. The browser demonstration is **in memory**, and restarting its server resets the sample data. Additional load tests, memory profiling, user registration, and configurable record/set limits are appropriate follow-up work for Phase 3.

## 4. Summary of the submitted work

The Phase 2 repository includes the Python workout tracker, AVL-tree index, command-line entry point, local browser UI/server, automated tests, manual QA test steps, requirements file, sample output, README, and implementation notes. This appendix explains how AI assistance was used and what the team actually verified. Team members should be able to explain and defend the code independently during the professor's walkthrough.

## 5. Commands used during verification

```powershell
py main.py
py -m unittest -v
py web_app.py
```

Open the browser demonstration at `http://127.0.0.1:8000` while the local web server is running.

---

**Integrity note:** This appendix summarizes the AI-assisted workflow visible in the project discussion. Team members should review it before submitting and correct any statement that does not accurately reflect their own participation or verification.
