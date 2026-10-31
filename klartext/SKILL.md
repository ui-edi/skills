---
name: klartext
description: Rewrites, audits or drafts text so it sounds like a real person instead of an AI, removing stock phrases, staged reveals and filler while keeping the writer's meaning and voice. Works in German and English. Use when the user says "Klartext", "plain talk", "humanize", "klingt nach KI", "sounds like AI", "entschwurble", "remove AI slop", or asks to make store texts, posts, READMEs, applications or emails sound natural.
---

# Klartext (Plain Talk)

*Inspired by "human-speak" by Nate Herk (github.com/nateherkai/human-speak). Independently rewritten and extended for German.*

## What this does

Text written with AI help often gives itself away: staged reveals, empty buzzwords, fake drama, a summary nobody asked for. Klartext removes those habits so the text sounds like a specific person with something real to say. It does not replace the writer's voice with polished corporate prose.

## Language

- Work in the language of the text. German text stays German, English stays English. Talk to the user in the language they write in.
- For German, keep the writer's regional spelling and register: Swiss German writers use "ss" instead of "ß" and Swiss quotes «…»; keep "du" or "Sie" exactly as the writer chose, and never mix them.
- Use the matching section of [references/patterns.md](references/patterns.md). German has its own giveaways (nominal style, inflated Anglicisms, stock openers); they are not just translations of the English ones.

## Pick the job

**Edit (default).** Rewrite the text with the smallest changes that fix it. Return the full edited text, then a short **What changed** list (3–6 lines, in the user's language). If the user wants clean copy only, skip the list.

**Audit.** When the user asks to check, scan or flag without rewriting: list each pattern found with the shortest useful quote and a one-line fix. No score, no guess about whether AI wrote it. If nothing is found, say so plainly and don't invent findings.

**Draft.** When the user asks for new text: follow the same rules, match the voice and material they gave, and never invent facts, numbers, quotes, experiences or opinions. Ask one short question only if the audience, format or goal is genuinely unclear.

## Before editing

1. Read the whole text first.
2. Find three things:
   - **the point:** what the reader should understand or do;
   - **the voice:** vocabulary, rhythm, humor, bluntness, dialect, level of polish;
   - **what must survive:** names, numbers, examples, mechanisms, opinions, intentional rough edges.
3. Check the text type. A store listing, a README, a job application, a social post and a chat message each have their own normal conventions (see "Text types" in the pattern library). Don't strip what the format legitimately needs.

## Editing rules

- **Keep the meaning.** Never add claims or make the writer sound more certain than they are.
- **Keep the voice.** Distinctive words, jokes, emojis the writer really uses, dialect and deliberate fragments stay.
- **Smallest effective edit.** Leave good human sentences alone. A text with little slop gets few changes.
- **Point first.** Cut throat-clearing. Keep personal setup when it creates context or character.
- **Concrete beats abstract.** Prefer facts, actions, names, numbers and consequences over labels like "important" or "innovative".
- **Plain verbs.** "is", "has", "can" are fine. In German, turn noun chains back into verbs ("Durchführung einer Optimierung" → "optimieren").
- **Same thing, same word.** Don't rotate synonyms for variety.
- **No reader-reaction narration.** Don't tell the reader that something is surprising, crucial or worth re-reading. Let the content do it.
- **Dashes:** don't use the long dash (— or –) as a default connector. Use a period, comma, colon or parentheses. One dash in a writer's own text is not a crime.
- **Formatting serves navigation,** not drama: no bold sprinkled through sentences, no headings over two-line sections, no bullet list for two sentences.

## Finish

Run the check in [references/check.md](references/check.md) and fix every failure before answering.

Rewording a pattern does not remove it. If a sentence still sets up a reveal, stages a contrast or stacks fragments, rewrite the thought as one direct sentence and check again.

## Boundaries

- This is an editing tool, not an AI detector. Never claim to know who or what wrote a text.
- Don't apply it to every reply automatically; only when asked or when the user's own task calls for it.
- Never change legal, medical or financial statements in a way that alters their meaning; flag them instead.
