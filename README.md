# Skills by ui-edi

Agent skills for Claude (claude.ai, Claude Code) and other AI agents that read `SKILL.md` files.
Agent-Skills für Claude (claude.ai, Claude Code) und andere KI-Agenten, die `SKILL.md`-Dateien lesen.

🇬🇧 [English](#english) · 🇩🇪 [Deutsch](#deutsch)

| Skill | What it does / Was er macht |
| --- | --- |
| [kreuzfeuer](kreuzfeuer/SKILL.md) | 🔥 Puts your idea under friendly crossfire, one question at a time, and logs every answer. · Nimmt deine Idee Frage für Frage ins Kreuzfeuer und protokolliert jede Antwort. |
| [klartext](klartext/SKILL.md) | 💬 Makes AI-assisted text sound like you again, in German and English. · Macht KI-Texte wieder menschlich, auf Deutsch und Englisch. |

---

## English

### Kreuzfeuer (Crossfire)

You have an idea in your head: a game, an app, a feature, a plan. Kreuzfeuer asks targeted questions until nothing important is left open, and writes every answer into a log the moment you give it. At the end you get a clean record with decisions, open points and a handover task list you can paste into your build chat.

- One question per message, easy to read on a phone
- A suggestion with every decision question, clearly marked as a suggestion
- Reads existing docs and code first, so it never asks what is already written down
- Speaks your language: write German, get grilled in German; write English, get English
- Stops the moment you say "stop"

**Start it** with something like: "Crossfire me on my new app idea" or "Grill me on the release plan".

### Klartext (Plain Talk)

Text written with AI help gives itself away: "It's not X, it's Y", "Here's the kicker", "No setup. No cost. Just results.", buzzwords, a recap nobody asked for. Klartext removes those habits and keeps your meaning, your voice and your jokes.

- Three jobs: **edit** (default), **audit** (list problems without rewriting), **draft** (write new text in your voice)
- A real German pattern library, not a translation: nominal style, «nahtlos», «Mehrwert», «Tauchen wir ein», chatbot residue
- Knows text types: store listings, READMEs, job applications, posts and UI texts each get their own rules
- Respects Swiss spelling (ss, «…») and your du/Sie choice
- Never invents facts and never claims to detect AI authorship

**Start it** with something like: "Klartext this store description" or "Does this README sound like AI?"

### Install

**claude.ai (web, desktop, mobile):** Download a skill folder (for example `kreuzfeuer` or `klartext`) as a ZIP and upload it under Settings → Capabilities → Skills. (Menu names can change; look for "Skills".)

**Claude Code:** Copy the folders into your skills directory:

```bash
git clone https://github.com/ui-edi/skills.git
cp -r skills/kreuzfeuer skills/klartext ~/.claude/skills/
```

**Other agents:** Point your agent at the skill's `SKILL.md`.

---

## Deutsch

### Kreuzfeuer

Du hast eine Idee im Kopf: ein Game, eine App, ein Feature, einen Plan. Kreuzfeuer stellt gezielte Fragen, bis nichts Wichtiges mehr offen ist, und schreibt jede Antwort sofort ins Protokoll. Am Ende hast du eine saubere Übersicht mit Entscheiden, offenen Punkten und einer Übergabe-Liste, die du direkt in deinen Bau-Chat kopieren kannst.

- Eine Frage pro Nachricht, gut lesbar am Handy
- Bei jeder Entscheidungsfrage ein Vorschlag, klar als Vorschlag markiert
- Liest zuerst vorhandene Dokumente und Code und fragt nie, was schon dasteht
- Spricht deine Sprache: Schreibst du Deutsch, wirst du auf Deutsch gelöchert
- Hört sofort auf, wenn du «Stopp» sagst

**Starten** zum Beispiel mit: «Nimm meine App-Idee ins Kreuzfeuer» oder «Grill mich zum Release-Plan».

### Klartext

KI-Texte verraten sich: «Es geht nicht um X, sondern um Y», «Und jetzt kommt der Clou», «Kein Stress. Kein Aufwand. Einfach Ergebnisse.», Buzzwords und ein Fazit, das keiner bestellt hat. Klartext entfernt diese Muster und behält deine Aussage, deine Stimme und deinen Humor.

- Drei Aufgaben: **überarbeiten** (Standard), **prüfen** (Probleme auflisten, ohne umzuschreiben), **schreiben** (neuer Text in deiner Stimme)
- Eine echte deutsche Muster-Sammlung, keine Übersetzung: Nominalstil, «nahtlos», «Mehrwert», «Tauchen wir ein», Chatbot-Reste
- Kennt Textarten: Store-Einträge, READMEs, Bewerbungen, Posts und App-Texte haben eigene Regeln
- Respektiert Schweizer Schreibweise (ss, «…») und deine Du/Sie-Wahl
- Erfindet nie Fakten und behauptet nie, KI-Texte zu erkennen

**Starten** zum Beispiel mit: «Mach Klartext aus dieser Store-Beschreibung» oder «Klingt dieses README nach KI?»

### Installation

**claude.ai (Web, Desktop, Handy):** Einen Skill-Ordner (z. B. `kreuzfeuer` oder `klartext`) als ZIP herunterladen und unter Einstellungen → Fähigkeiten → Skills hochladen. (Menünamen können sich ändern; such nach «Skills».)

**Claude Code:** Ordner in dein Skills-Verzeichnis kopieren:

```bash
git clone https://github.com/ui-edi/skills.git
cp -r skills/kreuzfeuer skills/klartext ~/.claude/skills/
```

**Andere Agenten:** Den Agenten auf die `SKILL.md` des Skills verweisen.

---

## Credits

Kreuzfeuer is inspired by the idea behind "grill-me" from [AIS-OS](https://github.com/nateherkai/AIS-OS) by Nate Herk (MIT). The text is written independently.
Kreuzfeuer ist von der Idee hinter «grill-me» aus [AIS-OS](https://github.com/nateherkai/AIS-OS) von Nate Herk (MIT) inspiriert. Der Text ist eigenständig geschrieben.

Klartext is inspired by [human-speak](https://github.com/nateherkai/human-speak) by Nate Herk (MIT). The text is written independently and extended with German patterns.
Klartext ist von [human-speak](https://github.com/nateherkai/human-speak) von Nate Herk (MIT) inspiriert. Der Text ist eigenständig geschrieben und um deutsche Muster erweitert.

## License

MIT, see [LICENSE](LICENSE).
