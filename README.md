# Skills by ui-edi

Agent skills for Claude (claude.ai, Claude Code) and other AI agents that read `SKILL.md` files.
Agent-Skills für Claude (claude.ai, Claude Code) und andere KI-Agenten, die `SKILL.md`-Dateien lesen.

🇬🇧 [English](#english) · 🇩🇪 [Deutsch](#deutsch)

| Skill | What it does / Was er macht |
| --- | --- |
| [kreuzfeuer](kreuzfeuer/SKILL.md) | 🔥 Puts your idea under friendly crossfire, one question at a time, and logs every answer. · Nimmt deine Idee Frage für Frage ins Kreuzfeuer und protokolliert jede Antwort. |

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

### Install

**claude.ai (web, desktop, mobile):** Download the `kreuzfeuer` folder as a ZIP and upload it under Settings → Capabilities → Skills. (Menu names can change; look for "Skills".)

**Claude Code:** Copy the folder into your skills directory:

```bash
git clone https://github.com/ui-edi/skills.git
cp -r skills/kreuzfeuer ~/.claude/skills/
```

**Other agents:** Point your agent at `kreuzfeuer/SKILL.md`.

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

### Installation

**claude.ai (Web, Desktop, Handy):** Den Ordner `kreuzfeuer` als ZIP herunterladen und unter Einstellungen → Fähigkeiten → Skills hochladen. (Menünamen können sich ändern; such nach «Skills».)

**Claude Code:** Ordner in dein Skills-Verzeichnis kopieren:

```bash
git clone https://github.com/ui-edi/skills.git
cp -r skills/kreuzfeuer ~/.claude/skills/
```

**Andere Agenten:** Den Agenten auf `kreuzfeuer/SKILL.md` verweisen.

---

## Credits

Kreuzfeuer is inspired by the idea behind "grill-me" from [AIS-OS](https://github.com/nateherkai/AIS-OS) by Nate Herk (MIT). The text is written independently.
Kreuzfeuer ist von der Idee hinter «grill-me» aus [AIS-OS](https://github.com/nateherkai/AIS-OS) von Nate Herk (MIT) inspiriert. Der Text ist eigenständig geschrieben.

## License

MIT, see [LICENSE](LICENSE).
