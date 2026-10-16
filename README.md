# Agent notes that go false: data and script

Data and code behind the post "Agent Notes About Open Bugs Go False. Fix Stories Don't." on
[launchwithben.com](https://launchwithben.com/learn/research/agent-notes-that-lie).

377 notes that coding agents wrote about files in 11 codebases (one an affiliate site, two trading
bots, the rest the author's own products), written April to October 2026, each checked against the code
as it stood in October 2026.

How the 377 came about: the full corpus was 886 notes. 427 were warnings (the `gotchas` and
`constraints` sections). 35 of those pointed at files that no longer exist and 15 were on the
LayerView tool's own files, which were not checked. 427 - 35 - 15 = 377. Those corpus counts are
not in the CSV, so the script cannot print them.

## Run it

```sh
python3 reproduce.py
```

Python 3 standard library only. It prints every rate, count and interval derived from the table, with
Wilson 95% intervals.

## The data

`notes-redacted.csv`: one row per note. No note text, project names or file paths.

| column | meaning |
|---|---|
| `id` | arbitrary row id |
| `project_class` | `own-product`, `affiliate-site` or `trading-bot` |
| `section` | `gotchas` or `constraints` |
| `quarter` | quarter the note was written (coarsened on purpose) |
| `kind` | RULE, DEFECT, STATE, PROCEDURE or INCIDENT, labelled blind from the note text |
| `kind2` | a second blind labeller, on a random 60-note sample only |
| `original` | `kept` or `stale`: first agent reading the code |
| `recheck` | TRUE, FALSE or UNCLEAR: a second agent reading the code, for all 46 DEFECT notes and 21 of the 41 INCIDENT notes (the one the first pass called stale plus a random 20 of the 40 it called kept). Blank means not re-checked |

## Limits

- Both readers of the code were agents that read it. Nobody ran it.
- The two readers disagreed on 14 of 67 notes and could not settle 1 more.
- The second reading did not cover the 25 notes of other kinds that the first pass called stale (16 rules,
  6 snapshots, 3 procedures), or about 285 other kept notes (326 kept, 41 re-read). The 13.5% first-pass
  rate is therefore rough. The first reader was too forgiving on open-bug notes (11 of the 21 it kept
  were false) and about right on fix stories (1 of the 20 it kept). The unread kept notes are mostly
  rules (225) and fix stories, which were never re-read, so how far they would move the total is untested. Using the second reading
  wherever it exists gives 60 of 377 (15.9%).
- The second readers were not told any first-pass verdict, but the batches were split by it: one set held
  only first-pass "stale" notes and the other only "kept" notes.
- Some second-reader TRUE verdicts were "main claim true, a detail now false". Those were scored TRUE.
- Samples: the 60-note labelling sample was drawn with a fixed random seed (7) and the 20 fix-story
  notes re-read with another (11), both reproduced at the bottom of `reproduce.py`.
- Open-bug notes cluster early (37 of 46 were written in Q2). Within Q2 alone the gap holds: 21 of 37
  open-bug notes false against 1 of 19 fix-story notes, on the first pass.
- One person's setup, and about a third of the notes come from a single project.

Corrections go in the commit history.

## Licence

Code (`reproduce.py`): MIT, see `LICENSE`. Data (`notes-redacted.csv`): CC BY 4.0, see `LICENSE-DATA`.
