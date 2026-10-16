#!/usr/bin/env python3
"""Reproduce every rate, count and interval derived from notes-redacted.csv in the post
"Agent Notes About Open Bugs Go False. Fix Stories Don't."  Corpus-level counts that are not in the
CSV (886 notes written, 427 warnings, 35 on deleted files, 15 on LayerView's own files) are in the README.

    python3 reproduce.py            # from this directory

The CSV has NO note text. Columns:
  id            arbitrary row id
  project_class own-product | affiliate-site | trading-bot
  section       gotchas | constraints
  quarter       2026-Q2 | 2026-Q3 | 2026-Q4: when the note was written
  kind          RULE|DEFECT|STATE|PROCEDURE|INCIDENT, labelled blind from the note text (labeller 1)
  kind2         second blind labeller, on a 60-note random sample only (blank otherwise)
  original      kept | stale: first pass, one agent reading the code
  recheck       TRUE|FALSE|UNCLEAR|blank: independent second reading of current code. Covers all 46
                DEFECT notes, plus 21 of the 41 INCIDENT notes (the one the first pass called stale
                and a random 20 of the 40 it called kept). Blank = not re-checked. The 25 notes of
                other kinds that the first pass called stale (16 RULE, 6 STATE, 3 PROCEDURE) were
                NOT re-checked.
"""
import csv, collections, os
from math import sqrt

def wilson(k, n, z=1.96):
    if n == 0: return (0.0, 0.0)
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n)
    a = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return 100 * (c - a) / d, 100 * (c + a) / d

rows = list(csv.DictReader(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "notes-redacted.csv"), newline="", encoding="utf-8")))
PER = {"DEFECT", "STATE", "PROCEDURE"}
def line(label, k, n):
    lo, hi = wilson(k, n)
    return f"{label:<44}{k:>4}/{n:<4} {100*k/max(n,1):5.1f}%   95% CI {lo:4.1f} to {hi:4.1f}"

print(f"notes: {len(rows)}")
print("\n== first pass (one agent reading code), by blind kind ==")
for kind in ["DEFECT", "STATE", "PROCEDURE", "RULE", "INCIDENT"]:
    r = [x for x in rows if x["kind"] == kind]
    print(line(kind, sum(x["original"] == "stale" for x in r), len(r)))
tot = sum(x["original"] == "stale" for x in rows)
print(line("ALL", tot, len(rows)))
p = [x for x in rows if x["kind"] in PER]; q = [x for x in rows if x["kind"] not in PER]
print(line("perishable (DEFECT+STATE+PROCEDURE)", sum(x["original"] == "stale" for x in p), len(p)))
print(line("durable (RULE+INCIDENT)", sum(x["original"] == "stale" for x in q), len(q)))

print("\n== second reading of the code ==")
rc = [x for x in rows if x["recheck"]]
print("re-checked notes:", len(rc), dict(collections.Counter(x["recheck"] for x in rc)))
s = [x for x in rc if x["original"] == "stale"]
print("first-pass 'stale' calls re-checked:", len(s), dict(collections.Counter(x["recheck"] for x in s)))
k = [x for x in rc if x["original"] == "kept"]
print("first-pass 'kept' calls re-checked:", len(k), dict(collections.Counter(x["recheck"] for x in k)))
for kind in ["DEFECT", "INCIDENT"]:
    r = [x for x in rc if x["kind"] == kind]
    print(f"  {kind}: re-checked {len(r)}  ->", dict(collections.Counter(x["recheck"] for x in r)))

print("\n== second-reading false rates, with intervals ==")
for kind in ["DEFECT", "INCIDENT"]:
    r = [x for x in rc if x["kind"] == kind]
    print(line(f"{kind} false on second reading", sum(x["recheck"] == "FALSE" for x in r), len(r)))
merged = sum((x["recheck"] == "FALSE") if x["recheck"] else (x["original"] == "stale") for x in rows)
print(line("ALL, second reading where it exists", merged, len(rows)))
dis = [x for x in rc if (x["original"] == "stale") != (x["recheck"] == "FALSE")]
print("readers disagree or unclear:", len(dis), "of", len(rc), "(", sum(x["recheck"] == "UNCLEAR" for x in dis), "of them UNCLEAR )")
print("\n== composition ==")
print("by project class:", dict(collections.Counter(x["project_class"] for x in rows)))
kf = [x for x in rc if x["original"] == "kept" and x["recheck"] == "FALSE"]
print("first-pass kept, second reading FALSE:", len(kf), dict(collections.Counter(x["kind"] for x in kf)))
print("kept notes: %d total, %d re-read (%s), %d not re-read" % (
    sum(x["original"] == "kept" for x in rows), len(k),
    ", ".join(f"{n} {c}" for c, n in collections.Counter(x["kind"] for x in k).items()),
    sum(x["original"] == "kept" for x in rows) - len(k)))
print("\n== age check: first-pass false rate within 2026-Q2 only ==")
for kind in ["DEFECT", "INCIDENT"]:
    r = [x for x in rows if x["kind"] == kind and x["quarter"] == "2026-Q2"]
    print(line(kind + " written in Q2", sum(x["original"] == "stale" for x in r), len(r)))

print("\n== agreement between two blind labellers (60-note sample) ==")
sm = [x for x in rows if x["kind2"]]
n = len(sm); a = [x["kind"] for x in sm]; b = [x["kind2"] for x in sm]
po = sum(i == j for i, j in zip(a, b)) / n
ca, cb = collections.Counter(a), collections.Counter(b)
pe = sum(ca[c] / n * cb[c] / n for c in set(a) | set(b))
print("labeller disagreements (labeller 1 -> labeller 2):", dict(collections.Counter(f"{x['kind']}->{x['kind2']}" for x in sm if x["kind"] != x["kind2"])))
print(f"n={n} exact agreement {po:.3f}  kappa {(po-pe)/(1-pe):.3f}")
ap = [i in PER for i in a]; bp = [j in PER for j in b]
po2 = sum(i == j for i, j in zip(ap, bp)) / n; p1 = sum(ap) / n; q1 = sum(bp) / n; pe2 = p1 * q1 + (1 - p1) * (1 - q1)
print(f"perishable-vs-durable only: agreement {po2:.3f}  kappa {(po2-pe2)/(1-pe2):.3f}")

import random
ids = {int(x["id"]) for x in rows if x["kind2"]}
random.seed(7)
print("\n== sample draws ==")
print("60-note labelling sample = random.seed(7); random.sample(range(1,378),60):", ids == set(random.sample(range(1, 378), 60)))
kept_inc = [int(x["id"]) for x in rows if x["kind"] == "INCIDENT" and x["original"] == "kept"]
random.seed(11)
drawn = {int(x["id"]) for x in rows if x["kind"] == "INCIDENT" and x["original"] == "kept" and x["recheck"]}
print("20 re-read fix stories = random.seed(11); random.sample(<40 kept INCIDENT ids in CSV order>,20):", drawn == set(random.sample(kept_inc, 20)))
