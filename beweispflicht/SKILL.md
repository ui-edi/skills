---
name: beweispflicht
description: "Evidence before every 'done': never claim work is finished, fixed, deployed or correct without fresh proof, and report the true status. Use before saying done, fixed, tests pass, «fertig», «läuft», «erledigt», «klappt», before delivering apps, games, APKs, files, numbers or research, before commits, deploys and releases, and when asked «funktioniert es?», «geht's jetzt?», «hast du's getestet?», «Beweis». Also use when the user asks to build, fix, update or deploy something («bau», «fix», «update», «neue Version»), so the result is verified before reporting back. Not for pure questions, explanations or brainstorming."
---

# Beweispflicht (Burden of Proof)

*Inspired by "verification-before-completion" from Superpowers by Jesse Vincent (github.com/obra/superpowers) and "doubt-driven-development" from Agent Skills by Addy Osmani (github.com/addyosmani/agent-skills), both MIT; see NOTICE. Independently rewritten and extended beyond code: web apps, games, Android builds, deploys, files, numbers, research and skills, including chat-only work from a phone.*

## What this does

A claim like "works now" costs nothing to write and a lot when it is wrong. Beweispflicht makes every status claim earn its place: first the proof, then the sentence. When proof is out of reach, the reply says so and hands the user a short test instead of a confident guess.

## Language

- Talk to the user in the language they write in, including the status words and the report labels below (both languages are given).
- German for Switzerland (de-CH): "ss", never "ß".

## The rule

**No claim of success without fresh evidence.**

- *Fresh* means produced after the last change in this conversation. Evidence from earlier still counts if nothing it covers has changed since.
- *Evidence* means the proof from the proof table was actually performed and its result looked at: command output, exit code, a rendered screenshot, an opened file, a recalculated number, a source read in this conversation. Feeling sure about your own work is not evidence.
- The rule covers every wording of success: "done", "should work now", «fertig», «müsste passen», "Perfect!", a ✅, and quietly moving on to the next task as if the last one worked.

## The proof loop

1. **Claim.** Write the exact claim in one line. If you cannot, you have a feeling, not a result.
2. **Proof.** Name what would show the claim is false if it were false. Pick the strongest proof you can actually run in this environment (see the proof table).
3. **Run.** Run it after the last change. A partial run is fine only if the claim is limited to what ran ("the 12 export tests pass", not "all tests pass").
4. **Read.** Read the whole result: exit code, failure count, warnings, console errors, the actual pixels.
5. **Report.** State the real status with the evidence. If the proof failed, say what failed; don't soften it.

## Evidence levels

Label claims that matter with how you know them. Never present a lower level as a higher one.

| Level | Meaning |
| --- | --- |
| **Gesehen / Verified** | The proof listed in the table for this deliverable was performed and its result checked. For a document that proof is opening and reading it; for a build it is running it. |
| **Geprüft / Inspected** | Looked at the code, file or data, but the table's proof could not be performed here. |
| **Angenommen / Assumed** | Expected from experience, not checked. Allowed only when labeled, never counts as done. |

## Proof table

The last column is the fallback when there is no shell or browser (for example chat-only on a phone). Label the result as that row says: Geprüft by default, Angenommen where the row says so. Where it says "Not possible", the status is Fertig mit Einschränkung (if the rest is done) or Blockiert (if that proof is required).

| Deliverable | Counts as proof (Gesehen) | Not enough | No shell/browser |
| --- | --- | --- | --- |
| Code / logic | Test or script run after the last edit, output read, exit code 0 | "Code looks right", linter only | Trace the logic by hand on 2 concrete inputs, including one edge case |
| Bug fix | Symptom reproduced first, gone after the fix | "Changed the line that caused it" | Explain the cause from the code, Prüf-Rezept for the original symptom |
| Regression test | Fails without the fix, passes with it | Passes once | Not possible: say so |
| Web app / PWA | Rendered at phone width (about 390 px) and desktop, screenshot looked at, console free of errors, main flow clicked through | HTML is valid, "opens fine" | Check markup, scripts and media queries; Prüf-Rezept on the user's phone |
| PWA offline / install | Service worker active, reload with network off still loads, manifest fields checked | Service worker file exists | Check manifest and cache list; Prüf-Rezept: flight mode, reopen |
| Game | Core loop played to a win or loss state, no console errors, balance numbers recalculated | "Game starts" | Recalculate balance in code if possible; Prüf-Rezept for one full round |
| Android build (APK/AAB) | Build exit 0, file present with plausible size, versionCode raised, signed with the release key, minSdk and permissions listed | Gradle sync passed | Check build files and manifest; Prüf-Rezept: install, open, run the main feature |
| Deploy (GitHub Pages, artifact, hosting) | Live URL loaded after the deploy and shows the new version (version string, changed text or cache-busted asset) | "Push succeeded" | Prüf-Rezept: open URL, hard reload, check the version |
| Git push / commit | Commit visible on the remote branch, working tree clean | "git push ran" | Not possible: say so |
| Generated images / sprites | Image opened and looked at: size, transparency, frame count, style matches the brief | "Image generated" | Ask the user for a screenshot if you cannot view it |
| Numbers / calculations | Recalculated in code | Mental arithmetic | Calculate step by step in writing and show the steps |
| Spreadsheet | Formulas recalculated, no error cells (#REF!, #DIV/0!), two values checked by hand | "Formulas inserted" | Check formula ranges by reading them; Prüf-Rezept |
| Document / file | File opened after writing, content and formatting read, links work | "File written" | Reread the full text you produced |
| Research / facts | Each key fact tied to a source read in this conversation | Memory, "commonly known" | Label as Angenommen and say it is unverified |
| Skill file | Frontmatter parses, name and description present, description holds the trigger words, instructions tried on one real example | "SKILL.md written" | Reread against the Agent Skills format; try it on one example in the chat |
| Delegated work (subagent, tool) | Diff or output checked yourself | The agent said "success" | Read the returned output yourself |

## Abnahme: check against the request

For tasks with several asks, or anything risky:

1. Re-read the user's original request and every change they asked for later.
2. Check each ask against evidence.
3. Report only what is not fully done (⚠️ limited, ❌ missing). If everything is done, one line says so.

A forgotten small ask is still a gap.

## When you cannot verify

Some proof is out of reach: the user's own phone, a store review, a login, sensors, a paid API.

- Name in one sentence what you could not verify and why.
- For testable things, hand over a **Prüf-Rezept / Quick test**: numbered steps and the expected result, under a minute if possible. For facts, name the source the user can check instead.
- The status is "done with limitation", never plain "done".
- Chat-only, low-stakes changes (wording, colors, a small layout tweak): the status line plus «ungetestet / untested» is enough. Collect the test steps into one combined Prüf-Rezept per batch or at the end of the session instead of one per edit.

Example:
> Not verifiable here: Bluetooth scanning on your phone.
> Quick test: 1. Install the APK. 2. Turn on Bluetooth. 3. Tap «Scan». Expected: your own earbuds appear within 10 seconds.

## Doubt round for risky claims

For claims that are non-obvious or expensive when wrong (security, data loss, money, health data, irreversible steps, "this is safe", "this scales"), add a doubt round before the claim stands:

1. Package the **artifact** (code, plan or text) and the **contract** (what it must do). Leave out your reasoning and your conclusion; handing over the conclusion invites agreement.
2. Review with the instruction "find what is wrong, do not validate". Use a fresh subagent in this session if one is available and give it only the package. Otherwise do a separate pass yourself and label it as a self-review.
3. Sort every finding: contract was unclear (fix the contract) / real problem (fix it, loop) / accepted trade-off (tell the user) / noise (note it, move on).
4. Stop when the findings are trivial, after 3 rounds, or when the user says ship it. Three rounds with real problems left means the artifact is not ready; tell the user.

Subagents inside this session are fine. Other AI CLIs, outside APIs or network calls need the user's explicit OK every time.

## Status words

Exactly one per final status, in the user's language:

- **Fertig / Done**: every ask has Gesehen evidence.
- **Fertig mit Einschränkung / Done with limitation**: every ask is done, but at least one part is only Geprüft or Angenommen; name it (Prüf-Rezept as described above).
- **Teilweise / Partial**: at least one ask is not done yet; list which.
- **Fehlgeschlagen / Failing**: the proof ran and failed; say what failed and the next step.
- **Blockiert / Blocked**: cannot continue; say what is missing and what the user can do.

If several fit, the first in this order wins: Fehlgeschlagen > Blockiert > Teilweise > Fertig mit Einschränkung > Fertig. Mention the others in the Offen line.

## Report format

Small change: one inline line, for example «Fertig, Build exit 0, App startet im Test.»

Multi-ask or risky work:

```
Status / Status: <one status word>
Beweis / Evidence: <1 to 3 lines: what was run or looked at, and the result>
Offen / Open: <only if something is unverified or missing, plus Prüf-Rezept>
```

Proof sits next to the claim. No celebration before the proof line.

## Red flags: stop and verify

- «sollte», «müsste», «eigentlich», "should", "probably", "seems to" in a status sentence
- Enthusiasm before evidence: "Perfect!", «Läuft!»
- About to deliver, commit, deploy or release with no proof run after the last edit
- Trusting a tool or subagent report without looking at the result
- Claiming "all" when only some tests, pages or files were checked
- "Just this once", "it's only a small change", wanting to wrap up a long session

## Excuses and answers

| Excuse | Answer |
| --- | --- |
| "I'm confident." | Confidence is not evidence. Run it. |
| "It's a one-line change." | One-line changes break builds every day. The proof is usually one command. |
| "The linter passed." | The linter does not run the app. |
| "It worked before my last edit." | Then the proof is stale. Run it again. |
| "The user can test it." | Only what you truly cannot test. Give a Prüf-Rezept for that part. |
| "Checking everything takes too long." | Check proportionally, but never claim more than you checked. |

## Proportionality

Match effort to stakes. A typo fix needs one look at the result and one inline line. A payment flow needs tests, a doubt round and an Abnahme. Questions, explanations and brainstorming need no proof at all; this skill is for claims about work that was made or changed.

Proof theater is a failure too: ten checks that cannot fail while the one that could is skipped. Pick the check that would catch the most likely mistake.

## Works well with (optional, if installed)

- **qa-tester** for deep testing: Beweispflicht is the gate before every "done", qa-tester the full inspection.
- **release-manager**: no release without a Fertig status.
- **kreuzverhoer / Kreuzfeuer**: grill the plan before building, Beweispflicht after.

## Final check

- [ ] Every success claim has evidence from after the last change.
- [ ] Gesehen only where the table's proof was actually performed.
- [ ] Multi-ask work: the original request was re-read and gaps are listed.
- [ ] Unverifiable parts are named, with a Prüf-Rezept.
- [ ] Exactly one status word; no «sollte» or "should" in it.
- [ ] Small change, short report. The reply fits a phone screen.
