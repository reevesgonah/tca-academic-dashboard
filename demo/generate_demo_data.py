"""
Generates a fully synthetic 3-term demo dataset that mirrors the STRUCTURE of
Total Care Academy's real Term 3, 2025 data (grades, subjects, class sizes,
subject difficulty, the KNEC-vs-END-TERM gap) WITHOUT using any real student
or teacher identity. This exists purely so the trend / continuity features
(term-over-term charts, roster churn, teacher reassignment) can be exercised
and demoed before real historical terms exist.

Every name here is fictional and explicitly checked against the real roster
(data/scores_long.csv, data/subject_teachers.csv) to guarantee zero overlap -
no synthetic score is ever attributed to a real, identifiable student or
teacher. Output lives entirely under demo/ and is never read by app.py
automatically.

Run: python3 demo/generate_demo_data.py
"""

import json
import random
from pathlib import Path

import numpy as np
import pandas as pd

random.seed(42)
np.random.seed(42)

HERE = Path(__file__).parent
REAL_SCORES = HERE.parent / "data" / "scores_long.csv"
REAL_TEACHERS = HERE.parent / "data" / "subject_teachers.csv"
OUT_DIR = HERE

# ---------------------------------------------------------------------------
# 1. School structure, mirrored from the real data (grades/subjects/streams/
#    class sizes/subject difficulty), but every identity below is invented.
# ---------------------------------------------------------------------------
GRADE_STRUCTURE = {
    2: {"streams": ["E", "N", "W"], "subjects": ["C/A", "CRE", "ENG.", "ENV.", "KIS.", "MATH"],
        "sizes": {"E": 20, "N": 20, "W": 22}, "bracket": "junior"},
    3: {"streams": ["E", "N", "W"], "subjects": ["C/A", "CRE", "ENG.", "ENV.", "KIS.", "MATH"],
        "sizes": {"E": 24, "N": 27, "W": 26}, "bracket": "junior"},
    4: {"streams": ["E", "W"], "subjects": ["C/A", "ENG.", "INT. SCI.", "KIS.", "MATH", "SST"],
        "sizes": {"E": 24, "W": 21}, "bracket": "middle"},
    5: {"streams": ["E", "W"], "subjects": ["C/A", "ENG.", "INT. SCI.", "KIS.", "MATH", "SST"],
        "sizes": {"E": 24, "W": 25}, "bracket": "middle"},
    6: {"streams": ["E", "W"], "subjects": ["C/A", "ENG.", "INT. SCI.", "KIS.", "MATH", "SST"],
        "sizes": {"E": 22, "W": 22}, "bracket": "middle"},
    7: {"streams": ["E", "W"], "subjects": ["AGRI.", "C/A", "CRE", "ENG.", "INT. SCI.", "KIS.", "MATH", "PRE-TECH", "SST"],
        "sizes": {"E": 19, "W": 18}, "bracket": "upper"},
    8: {"streams": ["E", "W"], "subjects": ["AGRI.", "C/A", "CRE", "ENG.", "INT. SCI.", "KIS.", "MATH", "PRE-TECH", "SST"],
        "sizes": {"E": 18, "W": 17}, "bracket": "upper"},
    9: {"streams": ["E", "W"], "subjects": ["AGRI.", "C/A", "CRE", "ENG.", "INT. SCI.", "KIS.", "MATH", "PRE-TECH", "SST"],
        "sizes": {"E": 17, "W": 16}, "bracket": "upper"},
}

SUBJECT_STATS = {  # (mean, std) sampled from the real END-TERM distribution
    "AGRI.": (76.6, 13.2), "C/A": (82.1, 17.8), "CRE": (88.1, 14.8), "ENG.": (81.1, 14.8),
    "ENV.": (94.2, 5.3), "INT. SCI.": (70.1, 18.2), "KIS.": (73.8, 17.3), "MATH": (76.1, 21.6),
    "PRE-TECH": (72.2, 20.6), "SST": (74.6, 17.7),
}
KNEC_SHIFT = -14.0  # real KNEC average sits ~14 points below END-TERM

TERMS = ["Term 1, 2025 (DEMO)", "Term 2, 2025 (DEMO)", "Term 3, 2025 (DEMO)"]

# ---------------------------------------------------------------------------
# 2. Fictional name pools, checked against the real roster
# ---------------------------------------------------------------------------
FIRST_NAMES = [
    "Amani", "Baraka", "Cheryl", "Denzel", "Esha", "Faraja", "Gideon", "Halima",
    "Imani", "Joska", "Kendi", "Lameck", "Mumbi", "Nasra", "Owino", "Pendo",
    "Quincy", "Rehema", "Sifa", "Tumaini", "Umi", "Victor", "Wanjiku", "Yusra",
    "Zawadi", "Alvin", "Beatrice", "Caleb", "Diana", "Elvis", "Fatuma", "George",
    "Hawa", "Irene", "Jael", "Kioko", "Lucy", "Maina", "Nafula", "Otieno",
    "Peris", "Ramadhan", "Sifuna", "Teresia", "Ulwiya", "Vivian", "Wafula", "Zena",
]
LAST_NAMES = [
    "Achieng", "Bett", "Chege", "Dena", "Eshiwani", "Gathoni", "Hamisi", "Injila",
    "Juma", "Kariuki", "Lomu", "Mburu", "Ndegwa", "Okoth", "Peter", "Rono",
    "Simiyu", "Tirop", "Wachira", "Yator", "Zablon", "Abdi", "Barasa", "Chepkoech",
    "Dzombo", "Emongor", "Furaha", "Gikonyo", "Hassan", "Ipara", "Jefwa", "Kilonzo",
]

with open("/tmp/real_names.json") as f:
    REAL_NAMES = set(json.load(f))
REAL_TEACHER_NAMES = set(pd.read_csv(REAL_TEACHERS)["TEACHER"].str.upper().str.strip())


def make_unique_names(n, used):
    out = []
    attempts = 0
    while len(out) < n and attempts < n * 50:
        attempts += 1
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}".upper()
        if name in REAL_NAMES or name in used:
            continue
        used.add(name)
        out.append(name)
    return out


def make_unique_teacher_names(n, used):
    out = []
    attempts = 0
    while len(out) < n and attempts < n * 50:
        attempts += 1
        name = random.choice(FIRST_NAMES).upper()
        if name in REAL_TEACHER_NAMES or name in used:
            continue
        used.add(name)
        out.append(name)
    return out


used_student_names = set()
used_teacher_names = set()

# ---------------------------------------------------------------------------
# 3. Teacher rosters per bracket (mostly stable across terms, with 1-2
#    reassignments introduced deliberately between terms)
# ---------------------------------------------------------------------------
junior_classes = [(g, s) for g, st in GRADE_STRUCTURE.items() if st["bracket"] == "junior" for s in st["streams"]]
n_junior_teachers = len(junior_classes)  # one class-teacher per junior class
junior_teacher_pool = make_unique_teacher_names(n_junior_teachers + 2, used_teacher_names)  # +2 spare for reassignment

specialist_pool = make_unique_teacher_names(16, used_teacher_names)

middle_upper_classes = [(g, s) for g, st in GRADE_STRUCTURE.items() if st["bracket"] in ("middle", "upper") for s in st["streams"]]


def build_specialist_assignment(rng_seed):
    """Assign each (grade, stream, subject) in middle/upper to a specialist
    teacher, reusing teachers across classes the way the real school does."""
    rng = random.Random(rng_seed)
    assignment = {}
    for grade, stream in middle_upper_classes:
        subjects = GRADE_STRUCTURE[grade]["subjects"]
        # each class is covered by a handful of teachers, each taking 1-3 subjects
        pool = specialist_pool.copy()
        rng.shuffle(pool)
        i = 0
        for subj in subjects:
            teacher = pool[i % len(pool)]
            assignment[(grade, stream, subj)] = teacher
            if rng.random() < 0.4:
                i += 1
    return assignment


def build_junior_assignment():
    return {(g, s): junior_teacher_pool[i] for i, (g, s) in enumerate(junior_classes)}


junior_assignment_by_term = {}
specialist_assignment_by_term = {}

base_junior = build_junior_assignment()
base_specialist = build_specialist_assignment(1)

for i, term in enumerate(TERMS):
    junior_assignment_by_term[term] = dict(base_junior)
    specialist_assignment_by_term[term] = dict(base_specialist)

# Minor reassignment: swap one junior class-teacher and one specialist
# subject-teacher between Term 1->2, and again between Term 2->3.
spare_junior = junior_teacher_pool[n_junior_teachers:]
swap_target_junior = junior_classes[0]
junior_assignment_by_term[TERMS[1]][swap_target_junior] = spare_junior[0]
junior_assignment_by_term[TERMS[2]][swap_target_junior] = spare_junior[0]

swap_target_specialist = middle_upper_classes[2]
some_subject = GRADE_STRUCTURE[swap_target_specialist[0]]["subjects"][0]
replacement_teacher = make_unique_teacher_names(1, used_teacher_names)[0]
specialist_assignment_by_term[TERMS[2]][(swap_target_specialist[0], swap_target_specialist[1], some_subject)] = replacement_teacher

# ---------------------------------------------------------------------------
# 4. Roster generation with small term-to-term churn (grade stays fixed
#    across these three terms - a student's grade only changes at year end)
# ---------------------------------------------------------------------------
student_counter = 1
roster_by_term = {}  # term -> list of dicts {STUDENT_ID, NAME, GRADE, STREAM, ABILITY}
ability_by_id = {}

for grade, struct in GRADE_STRUCTURE.items():
    for stream in struct["streams"]:
        base_size = struct["sizes"][stream]
        # Term 1 roster
        names = make_unique_names(base_size, used_student_names)
        term1_students = []
        for name in names:
            sid = f"DEMO-S{student_counter:04d}"
            student_counter += 1
            ability = np.random.normal(0, 1)  # persistent per-student ability offset
            ability_by_id[sid] = ability
            term1_students.append({"STUDENT_ID": sid, "NAME": name, "GRADE": grade, "STREAM": stream})
        roster_by_term.setdefault(TERMS[0], []).extend(term1_students)

        current = term1_students
        for term in TERMS[1:]:
            # ~4-6% churn: a couple of leavers, a couple of new joiners
            n_leave = max(0, int(round(len(current) * np.random.uniform(0.0, 0.06))))
            leavers_idx = set(np.random.choice(len(current), size=n_leave, replace=False)) if n_leave else set()
            survivors = [s for i, s in enumerate(current) if i not in leavers_idx]
            n_join = max(0, int(round(len(current) * np.random.uniform(0.0, 0.06))))
            new_names = make_unique_names(n_join, used_student_names)
            joiners = []
            for name in new_names:
                sid = f"DEMO-S{student_counter:04d}"
                student_counter += 1
                ability_by_id[sid] = np.random.normal(0, 1)
                joiners.append({"STUDENT_ID": sid, "NAME": name, "GRADE": grade, "STREAM": stream})
            current = survivors + joiners
            roster_by_term.setdefault(term, []).extend(current)

# ---------------------------------------------------------------------------
# 5. Score generation
# ---------------------------------------------------------------------------
rows = []
term_growth = {TERMS[0]: 0.0, TERMS[1]: 1.5, TERMS[2]: 3.0}  # slight improvement over the year

for term in TERMS:
    for student in roster_by_term[term]:
        grade, stream = student["GRADE"], student["STREAM"]
        subjects = GRADE_STRUCTURE[grade]["subjects"]
        ability = ability_by_id[student["STUDENT_ID"]]
        for subject in subjects:
            mean, std = SUBJECT_STATS[subject]
            mean = mean + term_growth[term]
            end_term_score = np.clip(np.random.normal(mean + ability * std * 0.4, std * 0.6), 0, 100)
            knec_score = np.clip(end_term_score + KNEC_SHIFT + np.random.normal(0, 6), 0, 100)
            for exam, score in [("KNEC", knec_score), ("END-TERM", end_term_score)]:
                rows.append({
                    "NAME": student["NAME"], "TERM": term, "EXAM": exam, "GRADE": grade,
                    "STREAM": stream, "SUBJECT": subject, "SCORE": round(float(score), 1),
                    "STUDENT_ID": student["STUDENT_ID"],
                })

scores_df = pd.DataFrame(rows)
scores_df.to_csv(OUT_DIR / "scores_long_demo.csv", index=False)
print(f"scores_long_demo.csv: {len(scores_df)} rows, {scores_df['NAME'].nunique()} unique names, "
      f"{scores_df['STUDENT_ID'].nunique()} unique student IDs")

# ---------------------------------------------------------------------------
# 6. Subject-teacher mapping, per term (demonstrates reassignment)
# ---------------------------------------------------------------------------
teacher_rows = []
for term in TERMS:
    for (grade, stream), teacher in junior_assignment_by_term[term].items():
        for subject in GRADE_STRUCTURE[grade]["subjects"]:
            teacher_rows.append({"TERM": term, "GRADE": grade, "STREAM": stream, "SUBJECT": subject, "TEACHER": teacher})
    for (grade, stream, subject), teacher in specialist_assignment_by_term[term].items():
        teacher_rows.append({"TERM": term, "GRADE": grade, "STREAM": stream, "SUBJECT": subject, "TEACHER": teacher})

teachers_df = pd.DataFrame(teacher_rows)
teachers_df.to_csv(OUT_DIR / "subject_teachers_demo.csv", index=False)
print(f"subject_teachers_demo.csv: {len(teachers_df)} rows, {teachers_df['TEACHER'].nunique()} unique teachers")

# ---------------------------------------------------------------------------
# 7. Class-teacher listing per term (homeroom - for junior this is the same
#    person as the subject teacher; for middle/upper, pick one of that
#    class's specialists as homeroom)
# ---------------------------------------------------------------------------
class_teacher_rows = []
for term in TERMS:
    for (grade, stream), teacher in junior_assignment_by_term[term].items():
        class_teacher_rows.append({"TERM": term, "GRADE": grade, "STREAM": stream, "TEACHER": teacher})
    for grade, stream in middle_upper_classes:
        first_subject = GRADE_STRUCTURE[grade]["subjects"][0]
        homeroom = specialist_assignment_by_term[term][(grade, stream, first_subject)]
        class_teacher_rows.append({"TERM": term, "GRADE": grade, "STREAM": stream, "TEACHER": homeroom})

class_teachers_df = pd.DataFrame(class_teacher_rows)
class_teachers_df.to_csv(OUT_DIR / "class_teachers_demo.csv", index=False)
print(f"class_teachers_demo.csv: {len(class_teachers_df)} rows")

# ---------------------------------------------------------------------------
# Sanity checks: zero overlap with real identities
# ---------------------------------------------------------------------------
overlap_students = set(scores_df["NAME"].unique()) & REAL_NAMES
overlap_teachers = set(teachers_df["TEACHER"].unique()) & REAL_TEACHER_NAMES
assert not overlap_students, f"Student name collision with real roster: {overlap_students}"
assert not overlap_teachers, f"Teacher name collision with real roster: {overlap_teachers}"
print("Zero-overlap check passed: no synthetic identity matches a real student or teacher.")
