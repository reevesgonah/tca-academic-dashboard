# Total Care Academy — Analytics Dashboard

A Streamlit rebuild of the Power BI academic dashboard, deployable as a shareable
weblink instead of requiring a Power BI license per viewer.

## Pages

**🏫 School Overview** — the landing page. School-wide health check only:
headcounts, pass rate, average total score term-over-term (a single point for
now, extends automatically as terms are added), and the three "landscape"
charts — score distribution by grade, subject averages, and average total
score by class. Nothing here drills into individual students or classes;
that's what the next two pages are for.

**📚 Grade Explorer** — pick a grade, optionally a stream. Shows a subject ×
stream heatmap (spot a weak subject or stream fast), subjects ranked for that
grade, top/bottom N students, an at-risk list scoped to that grade, and —
when a specific stream is selected — the subject-teacher table for that
class with a **"Focus these teachers"** button that jumps straight to the
Teacher Performance tab with those teachers pre-selected.

**🎓 Student Profile** — its own page now. Search a student, see a bar chart
of raw KNEC vs END-TERM scores per subject, a line chart of movement between
the two exams (replaces the old bar-chart version — a line reads as movement
much more clearly, and the same chart will extend to real term-over-term
trends once more terms are loaded), and a radar chart giving a directional
read on subject-cluster strength across the three CBC pathway clusters
(STEM / Social Sciences / Arts & Sports) — a heuristic, not an official
KICD placement.

**👩‍🏫 Teacher Performance** — bracket-first: Junior (Grades 2–3), Middle
(4–6), Upper (7–9), matching how the headteacher actually evaluates staff —
never across brackets. Junior teachers (one teacher, one class, all subjects)
are compared on raw class average, since every junior teacher covers an
identical subject set. Middle/Upper teachers (subject specialists shared
across classes) are compared by z-score normalized within subject *and*
within bracket, so a teacher on a harder subject or weaker stream isn't
penalized against one teaching an easier subject. A multiselect lets you
narrow the ranking chart and workload/performance scatter to specific
teachers — the slicer-style comparison from the Power BI version.

## Why some things aren't fully built out yet

Real term-over-term trend lines, an early-warning "declining student" view,
and teacher trajectories all need multiple terms of history. Only Term 3,
2025 survived, so those are shown as single-point placeholders that are
structurally ready to fill in — every chart that should eventually show a
trend already reads off `TERM` as a real column, not a hardcoded value.

**On tracking students and teachers across terms/grades**: right now
students and teachers are identified by name. That's fine for one term, but
it will eventually break — duplicate names, spelling drift, a teacher
reassigned mid-year. `data_utils.py` already falls back to a `STUDENT_ID`
column if one exists in the uploaded file, defaulting to name if not — so
adding a persistent ID (ideally an admission number) to a future term's
export is a drop-in improvement, not a rewrite. Worth doing before this
becomes the primary tool used in meetings across multiple years.

## Demo dataset for testing trends before real historical data exists

`demo/` contains a fully synthetic 3-term dataset — invented student and
teacher names only, structurally mirroring the real school — for testing the
trend, roster-churn, and teacher-reassignment features safely. See
`demo/README.md` for what it models and how to load it. It's never read by
the app automatically.

## Branding

Uses the TCA crest (`assets/logo.jpeg`) as the page icon, sidebar header, and
login screen. Styling is otherwise back to Streamlit's defaults, with one
kept addition: a light-blue background on the KPI/metric cards.

## Running locally

```bash
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# edit secrets.toml and set APP_PASSWORD to the real staff password
streamlit run app.py
```

## Deploying (Streamlit Community Cloud — free)

1. Push this folder to a GitHub repo (can be private).
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with GitHub,
   and point it at the repo, branch, and `app.py`.
3. In the app's **Settings → Secrets**, paste:
   ```toml
   APP_PASSWORD = "the real staff password"
   ```
4. Deploy. You'll get a `https://yourapp.streamlit.app` link to share with staff.

**App Link:** [https://total-care-academy-academic-dashboard.streamlit.app/](https://total-care-academy-academic-dashboard.streamlit.app/)

**Important — this is student data.** The password gate is a basic deterrent,
not strong security. For a small family-run school this may be an acceptable
trade-off, but worth layering on Streamlit Community Cloud's built-in viewer
restriction (Settings → Sharing → restrict to specific emails) before wider
rollout.

## Keeping real data out of this repo (recommended before deploying)

By default this app reads `data/*.csv` directly, which means those files
would need to be in this repo — public or private — for the deployed app to
see them. `.gitignore` already stops them from being committed, but that
just means you'd need another way to get the data to the deployed app.

The cleaner option: point the app at a **separate, private GitHub repo**
that holds only the data, so real student records never touch this
project's history at all. See `.streamlit/secrets.toml.example` for the
full one-time setup (a second private repo + a read-only access token).
Once `[data_source]` is configured in your deployed app's Secrets, the app
fetches that term's data at runtime and re-checks for updates hourly — so
updating the data just means updating that other repo, no redeploy needed.

Until you set that up, the app works exactly as before, reading `data/`
locally — nothing breaks if you skip this section for now.

## Adding a new term's data

Every term, export the records in the same long format used here:

| NAME | TERM | EXAM | GRADE | STREAM | SUBJECT | SCORE |
|---|---|---|---|---|---|---|

(Add a `STUDENT_ID` column too, once available, to make cross-term tracking
robust — see above.)

Upload it from the sidebar (**"➕ Add a new term's data"**). This appends it
for the current browser session only — it does **not** persist across
restarts or other users' sessions, since Streamlit Cloud's filesystem is
ephemeral. To make new terms permanent for everyone:
- Simplest: replace `data/scores_long.csv` in the GitHub repo with the
  combined file (old + new term rows) and redeploy — a 2-minute manual step
  each term.
- Better long-term: swap the CSV for a small hosted database (SQLite file
  committed to the repo, or a free-tier Postgres like Supabase/Neon) so
  uploads persist automatically. Worth doing once the trend views are the
  main draw of the dashboard.

## File structure

```
app.py                          # Streamlit UI — four tabs
data_utils.py                   # loading, joins, bracket-aware teacher normalization, risk/rank/cluster logic
assets/logo.jpeg                # TCA crest — swap this file to rebrand
data/scores_long.csv            # Term 3, 2025 — long format (NAME, TERM, EXAM, GRADE, STREAM, SUBJECT, SCORE)
data/subject_teachers.csv       # GRADE, STREAM, SUBJECT -> TEACHER
data/class_teachers.csv         # GRADE, STREAM -> class teacher
requirements.txt
.streamlit/secrets.toml.example # rename to secrets.toml and fill in APP_PASSWORD
```
