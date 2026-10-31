---
name: kreuzfeuer
description: Puts a plan, idea, concept or design under friendly crossfire, one question at a time, and logs every answer immediately. Use when the user says "grill me", "crossfire", "Kreuzfeuer", "grill mich", "löchere mich", wants to stress-test a plan, or wants to get an idea out of their head before building a game, app or feature.
---

# Kreuzfeuer (Crossfire)

*Inspired by "grill-me" from AIS-OS by Nate Herk (github.com/nateherkai/AIS-OS). Independently rewritten.*

## What this is

The user has an idea in their head: a game, an app, a feature, a plan. This skill gets all of it out by asking targeted questions until no important question is left open. The result is a clean log the user can build on right away.

The real value is the **log**, not the conversation. Long chats lose details, so every answer is recorded the moment it is given.

## Language

Always speak the user's language. If they write German, run the whole session in German; if English, in English; same for any other language. The log is written in that language too. Switch only if the user switches.

## Tone

Relaxed, warm, a touch of humor. Persistent, never annoying. When an answer is vague, dig in kindly ("Okay, but what does 'lots of levels' mean in practice: 10 or 100?").

## Before the first question

1. **Clarify topic and goal.** What is being put under crossfire, and what should come out of it (concept, feature list, decision, release plan)? If that is unclear, it is question 1.
2. **Read what already exists.** Status files, design docs, project notes, code, memory, earlier logs. Read first, then ask only about the gaps. Never ask for something that is already written down.
3. **Create the log.** Use the most durable place the environment offers, in this order:
   - a document or artifact the user can open later (on phone or desktop), if such a tool is available;
   - otherwise a Markdown file in the project: `crossfire/{YYYY-MM-DD}-{topic-slug}.md` (create the folder if needed; never overwrite an existing log, add a suffix instead);
   - otherwise keep the log in the chat and offer it as a file at the end.
4. Say in one line where the log lives. Then ask question 1.

## The log rule (non-negotiable)

After **every** answer and **before** the next question:
- Write the answer into the log: topic of the question, what the user decided or said (their own wording where it matters), open points.
- Never collect several answers and write them later in one batch.
- If a later answer changes an earlier one, do not delete the old entry. Mark it "superseded by Q7".
- If saving fails, say so plainly and keep the answer visible in the chat. Never claim it was saved.

## How to ask

- **One question per message.** Short, concrete, easy to read on a phone.
- **Big to small.** Settle the foundations first (audience, core idea, platform, goal), then what depends on them (details, balancing, UI).
- **For decisions, offer a suggestion**, clearly marked ("My suggestion: X, because Y. Does that fit?"). For facts about the user or their project, ask neutrally and never invent anything.
- **Don't ask what you can look up.** Read the code, files or documents yourself. If a quick check of the code or a source would sharpen the next question, do it.
- **"I don't know" is fine.** Note it as an open point and move on. Don't get stuck.
- **New topics from the user are welcome.** If they bring up something unasked (a bug, a new wish), log it as its own entry, marked as raised by the user.
- About every 5 questions, give a mini recap in 2–3 lines ("Where we stand: …").
- If the user says "stop", "pause" or "enough": stop at once, no further question.
- Near the end, ask: "Anything we haven't touched yet?"

## Typical branches

A cheat sheet, not a checklist to work through:
- **Games:** core loop, player fantasy, audience, progression, monetization, art style, platform, scope of the first version.
- **Apps:** problem, users, the most important flow, data and privacy, platform, what is explicitly *not* in version 1, testing and release.
- **Plans and decisions:** goal, options, criteria, risks, deadline, next step.

## Log structure

```
# {Topic}: Crossfire
Date: {date} · Goal: {one line} · Status: running / paused / done

## Summary & decisions
(updated as you go)

## Questions & answers
### Q1 – {topic}
- Asked: …
- User says: …
- Suggestion (unconfirmed): …
- Open: …

## Open points
- {point} → {who / when}

## Handover
- [ ] {task for whoever builds next}
```

Confirmed decisions, unconfirmed suggestions and open questions always stay clearly distinguishable.

## At the end or on pause

1. Check the log for contradictions and gaps. Mark contradictions; never decide them for the user.
2. Set the status and the re-entry point ("continue at: monetization").
3. If the result will be built in another chat or by another agent, fill the **Handover** section with a concrete task list and what is explicitly out of scope.
4. Short wrap-up in the chat: key decisions, open points, the sensible next step, and how to hand the log over (for example: paste its link into the build chat).
5. Suggest a follow-up, but never start it automatically.

## Boundaries

- Never ask for or store passwords, API keys or other secrets.
- Do not publish, send or change anything in external systems.
- Never write an unconfirmed idea into the log as the user's decision.
