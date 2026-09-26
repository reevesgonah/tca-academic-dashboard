# Demo dataset — fully synthetic, for testing only

This folder contains a **fully fictional** 3-term dataset that mirrors the
*structure* of the real Term 3, 2025 data (same grades, subjects, class
sizes, subject difficulty, and the real KNEC-vs-END-TERM gap) but uses
**invented student and teacher names only**. It exists to let you test-drive
the trend, roster-churn, and teacher-reassignment features before real
historical terms exist.

**No synthetic score is attributed to any real, identifiable person.** The
generator (`generate_demo_data.py`) cross-checks every generated name against
the real roster and hard-fails if there's ever a collision — see the
"Zero-overlap check passed" line when it runs.

## What it models

- **Term 1, 2025 (DEMO) → Term 2 → Term 3**, same academic year, so grades
  don't change between them (grade only advances at year-end) — just small
  enrollment churn (~3–6% leavers/joiners per term, matching normal
  mid-year transfers).
- **A gentle, realistic improvement** in average scores term over term
  (~10 points total across the year), so the term-over-term trend chart on
  the School Overview page has something to show.
- **One deliberate teacher reassignment** in each bracket: a Junior
  class-teacher (Grade 2E) changes between Term 1 and Term 2, and a
  Middle/Upper subject-teacher changes between Term 2 and Term 3 — so you
  can see how the app would (eventually) reflect real staff changes.
- Every student carries a synthetic but persistent `STUDENT_ID`
  (`DEMO-S0001`, etc.) — this is also a working preview of what the app can
  do once your real records have proper student IDs instead of relying on
  name matching.

## Files

- `scores_long_demo.csv` — same schema as production (`NAME, TERM, EXAM,
  GRADE, STREAM, SUBJECT, SCORE`), plus `STUDENT_ID`.
- `subject_teachers_demo.csv` — same as production's `subject_teachers.csv`,
  plus a `TERM` column. The app now supports a `TERM` column here (it didn't
  before) specifically so this demo's reassignment scenario displays
  correctly — and the same support is live for a real per-term mapping file
  in future, with no further code changes needed.
- `class_teachers_demo.csv` — homeroom listing per class per term.
- `generate_demo_data.py` — the generator itself, fully reproducible
  (`python3 demo/generate_demo_data.py`, fixed random seed).

## How to test with it

**Scores (easy — no file changes needed):** open the app, use the sidebar's
**"➕ Add a new term's data"** uploader, and upload `scores_long_demo.csv`.
All three demo terms will appear in the Term selector, and School Overview's
trend chart will show a real 3-point line instead of a single point.

**Teacher reassignment (requires a temporary local file swap):** the sidebar
uploader only accepts score files today, not teacher-mapping files, so to
see the reassignment reflected in the Teacher Performance tab:
1. Back up the real `data/subject_teachers.csv` and `data/class_teachers.csv`.
2. Copy `subject_teachers_demo.csv` → `data/subject_teachers.csv` and
   `class_teachers_demo.csv` → `data/class_teachers.csv`.
3. Restart the app, upload the demo scores, and switch between the three
   demo terms on the Teacher Performance tab to see Grade 2E's teacher
   change from PERIS to OWINO.
4. Restore your real files afterward.

(If this turns out to be a feature you'd use often — not just for this one
test — it's a small addition to give teacher mappings their own uploader
too, same as scores. Worth doing once real multi-term data exists.)
