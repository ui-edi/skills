---
name: bauplan
description: "Turns a feature, fix or project idea into a build plan of small, checkable steps: exact files, a proof per step (also testable from a phone), a stop rule, and a running app after every step; then executes it step by step. Use for «Bauplan», «plan das», «zerleg das», «wie gehen wir vor?», before multi-file changes, and when a task feels too big to start."
---

# Bauplan (Build Plan)

*Inspired by "writing-plans" from Superpowers by Jesse Vincent (github.com/obra/superpowers, MIT) and "planning-and-task-breakdown" from Agent Skills by Addy Osmani (github.com/addyosmani/agent-skills, MIT). Independently rewritten; adds phone-first proofs, stop rules, data safety and a handover link. See NOTICE.*

## What this does

Big changes fail in the middle: half the files are new, nothing runs, and nobody knows which part broke. A Bauplan cuts the work into steps that each end with a working app and a proof. You always know where you are, can stop after any step, and the next chat can continue without guessing.

## Language

- Talk to the user in the language they write in. de-CH: "ss", never "ß".
- The plan file is written in the user's language; code identifiers stay as they are.

## When to plan, when not

Plan when the work touches more than two files, takes more than one session, changes saved data, adds a dependency or external service, or the user asks for a plan.

Skip the plan for a one-file change with an obvious result; just do it and prove it.

**Kurzplan** for small work (up to about five files, one session, no saved-data change, no new service): only Ziel, 1–3 steps each with Dateien, Beweis and Fertig wenn, and the Log. Skip Stolperfallen, spike and milestones. Switch to the full plan as soon as one of those conditions breaks.

If the goal itself is still unclear (who, what, why), clear that first, for example with the skill Kreuzverhör/Kreuzfeuer if installed. A plan cannot fix a fuzzy goal.

## Before writing

1. **Read first, write nothing.** Read the request, any spec or `docs/STATUS.md`, and the code the change will touch. Note existing patterns and names.
2. **Check for an existing plan.** If `docs/PLAN.md` exists with open steps for different work, stop and ask: finish it, or park it. Parking means setting `Status: geparkt` and moving the file to `docs/plans/<date>-<name>.md`. Never overwrite or delete open steps.
3. **Collect the acceptance criteria.** What must be true when it is done? Take them from the user or the spec; where none exist, propose 3–6 and mark them as proposals.
4. **Find the biggest unknown.** A library that might not work on Android, an API limit, a performance question. It goes first as a time-boxed spike (see below).

## The plan file

Always write `docs/PLAN.md` as a file. With a project folder it goes into `docs/`; when working from a phone with a project ZIP, it goes into the new ZIP; without any project yet, deliver it as a file the user keeps with the project. A plan that only lives in the chat is lost in the next chat. Keep it short: a plan longer than the code it describes has written the code instead.

The headings and status words below stay exactly as written (German), because other skills such as project-handover read them. Everything else is written in the user's language. Status is one of `aktiv`, `geparkt`, `abgeschlossen`.

Only names of keys and environment variables go into the plan and the Log, never their values; strip secrets from pasted command output.

```markdown
# Bauplan: <feature>
Stand: <date> · Ziel-Version <x.y.z> · Status: aktiv

## Ziel
One sentence: what the user can do afterwards.

## Abnahme (acceptance criteria)
- [ ] A1 …   (each one testable)
- [ ] A2 …

## Nicht dabei (non-goals)
- …

## Rahmen (constraints)
- Platform, versions, libraries allowed, data that must survive, budget limits

## Stolperfallen (likely to bite users)
- Up to 5 inputs or situations the criteria don't mention but users will hit
  (empty list, no network, app killed mid-way, very long text, permission denied).
  Each one gets a check inside the step that owns it.

## Schritte
### S1 · <title>            [Grösse S] [braucht: –]
- Warum: …
- Dateien: new `src/x.js`, change `src/app.js` (function `start()`)
- Schnittstelle: provides `loadRounds(): Round[]` (only when later steps use it)
- Beweis: <command and expected result> or Prüf-Rezept: 1. … 2. … Expected: …
- Fertig wenn: <one observable condition>
- Zurück: how to undo (revert commit, feature flag off)

## Offene Fragen
- …

## Log
- <date> S1 ✅ Gesehen: <one line proof>
- <date> S2 ✅ Bestätigt: <the user ran the Prüf-Rezept, result>
- <date> S3 ⏳ wartet auf Prüf-Rezept
```

## Rules for steps

- **Vertical slices.** Each step delivers something usable end to end (data + logic + screen for one small case), not "all data first, then all screens".
- **A running app after every step.** Never leave the project broken between steps. If a change needs several steps, hide it behind a flag or keep the old path until the new one is proven.
- **Small.** One focused chunk of work, at most about five files. If the title needs "and", it is two steps. 3–12 steps per plan; more means split into milestones, each with its own plan.
- **Exact.** Name the files, the functions or screens, and the values from the spec. Lines that decide nothing ("handle edge cases", "add tests", "TBD") are not allowed; either decide or move it to Offene Fragen.
- **One proof per step,** written before the step is built:
  - with a shell: the command and the expected output;
  - without one (phone): a Prüf-Rezept the user can do in about a minute, with the expected result;
  - mark steps that need a desktop, Mac or CI with `[braucht Rechner]` so they don't surprise anyone.
- **Order:** spike for the biggest unknown → foundations other steps use → the core user flow → edge cases and Stolperfallen → polish → release steps. Risky things early, cosmetics late.
- **Saved data is sacred.** Any step that changes stored data, save games or settings formats gets: a version number for the format, a migration from the old format, a test with a copy of a save file in the old format (made-up test data, never live user data), and an automatic backup of the old data before migrating. The old app version must at least recognize a newer format and refuse politely instead of overwriting it. For these steps, «Zurück» means restoring the backup, not just reverting the code. This step comes before any step that relies on the new format.
- **Secrets.** If a step touches API keys, logins or payments, it states where the key lives (server only) and includes a concrete check that no key ends up in the build: scan the build folder or app package for key patterns (the scanner of the skill Schleuse does this, also for APKs) and search it for the names of the secret variables. Follow the skill app-studio's Schlüssel-Schutz if installed.
- **New dependencies** get their own step, with a check of origin and license (skill Schleuse if installed).

## Spike: answering the biggest unknown first

A spike is a throw-away experiment with a time box (for example "one session"). It answers one question ("Can Web Bluetooth read a heart-rate strap on Android Chrome?") and ends with a yes/no and a note in the Log. Its code is not kept unless the plan says so. If the answer is no, replan before building anything else.

## Check the plan before showing it

1. **Coverage:** every acceptance criterion maps to at least one step; every Stolperfalle has an owning step.
2. **Names:** a function, file or field is called the same in every step that uses it.
3. **Proofs:** every step has a proof that could actually fail.
4. **Proportion:** mostly decisions, little code. Replace long code blocks with signatures and expected results.
5. **Phone reality:** steps the user can't verify from the phone are marked, and there is a way to verify them (CI, a test build link, a screen recording).

Then show the plan in a few lines (goal, number of steps, the first step, open questions) and ask the user to approve or change it. Do not start building until they agree, unless they already said "just do it".

## Building the plan

One step at a time:

1. Re-read the step and the files it names.
2. Build only that step. Anything new that comes up becomes a new step or an Offene Frage, not a silent extra.
3. Run the step's proof and record it in the Log. Tick the step only with real evidence:
   - **✅ Gesehen** when Claude ran the proof and saw it pass;
   - **✅ Bestätigt** when the user ran the Prüf-Rezept and reported the expected result;
   - otherwise **⏳ wartet auf Prüf-Rezept**: the step stays open, and steps that depend on it wait. Independent steps may continue.
   Code that was only read or assumed to work never gets a tick (evidence labels as in the skill Beweispflicht, if installed).
4. Commit or deliver per step, with the step ID in the message (`S3: Runden aus localStorage laden`).
5. At a checkpoint (every 2–3 steps, and after the core flow) run all earlier proofs again in short form, so a new step didn't break an old one.

**Stop rule.** Stop and replan instead of pushing on when:
- a step's proof fails twice after fixes,
- a step grows to about twice its planned size,
- the spike or a step shows an assumption of the plan was wrong,
- the user changes the goal.

Then: write what was learned in the Log, adjust or reorder the remaining steps, show the change in one or two sentences, and continue only after the user agrees.

## Handover

The plan is a project document. At the end of a session (or with the skill project-handover, if installed): `docs/STATUS.md` names the active plan and the next open step; the Log in `docs/PLAN.md` shows what was proven. When all steps and acceptance criteria are done, set `Status: abgeschlossen`, move the important decisions into `docs/DECISIONS.md`, and archive the file as `docs/plans/<date>-<name>.md`. The next plan starts a fresh `docs/PLAN.md`; archived plans are never overwritten.

## Final check

- [ ] Code was read before planning; no open plan was overwritten (parked or finished plans are archived in `docs/plans/`).
- [ ] The plan exists as a file, contains no secret values, and steps are only ticked with Gesehen or Bestätigt.
- [ ] Each acceptance criterion and Stolperfalle has an owning step.
- [ ] Every step: exact files, a proof that can fail, a "fertig wenn", a way back.
- [ ] The app runs after every step; saved data is migrated, never lost.
- [ ] Steps needing a desktop or CI are marked.
- [ ] The user approved the plan before building started.
