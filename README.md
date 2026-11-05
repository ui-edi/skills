# Skills by ui-edi

Agent skills for Claude (claude.ai, Claude Code) and other AI agents that read `SKILL.md` files.
Agent-Skills für Claude (claude.ai, Claude Code) und andere KI-Agenten, die `SKILL.md`-Dateien lesen.

🇬🇧 [English](#english) · 🇩🇪 [Deutsch](#deutsch)

| Skill | What it does / Was er macht |
| --- | --- |
| [kreuzfeuer](kreuzfeuer/SKILL.md) | 🔥 Puts your idea under friendly crossfire, one question at a time, and logs every answer. · Nimmt deine Idee Frage für Frage ins Kreuzfeuer und protokolliert jede Antwort. |
| [klartext](klartext/SKILL.md) | 💬 Makes AI-assisted text sound like you again, in German and English. · Macht KI-Texte wieder menschlich, auf Deutsch und Englisch. |
| [drehbuch](drehbuch/SKILL.md) | 🎬 Scroll-driven landing pages written like a screenplay, as one HTML file that works on phones. · Scroll-Landingpages wie ein Drehbuch, als eine HTML-Datei, die am Handy funktioniert. |
| [beweispflicht](beweispflicht/SKILL.md) | 🧾 No "done" without proof: the agent shows evidence or hands you a one-minute test. · Kein «fertig» ohne Beleg: Der Agent zeigt den Beweis oder gibt dir einen Test für eine Minute. |
| [schleuse](schleuse/SKILL.md) | 🛂 Checks foreign skills, plugins and repos before you install them, with a read-only scanner. · Prüft fremde Skills, Plugins und Repos vor der Installation, mit einem Scanner, der nur liest. |
| [bauplan](bauplan/SKILL.md) | 🧱 Cuts a feature into small steps, each with a proof, and the app keeps running after every step. · Zerlegt ein Feature in kleine Schritte mit Beweis, und die App läuft nach jedem Schritt. |
| [stilkompass](stilkompass/SKILL.md) | 🧭 Finds a design direction that fits your product, with calculated contrast and a color-blindness check. · Findet eine passende Design-Richtung, mit nachgerechnetem Kontrast und Farbenblindheits-Check. |

---

## English

### Kreuzfeuer (Crossfire)

You have an idea in your head: a game, an app, a feature, a plan. Kreuzfeuer asks targeted questions until nothing important is left open, and writes every answer into a log the moment you give it. At the end you get a clean record with decisions, open points and a handover task list you can paste into your build chat.

- One question per message, easy to read on a phone
- A suggestion with every decision question, clearly marked as a suggestion
- Reads existing docs and code first, so it never asks what is already written down
- Speaks your language: write German, get grilled in German; write English, get English
- Stops the moment you say "stop"
- Ends with the smallest first step you can already test, and a handover list in order, each task with a "done when"

**Start it** with something like: "Crossfire me on my new app idea" or "Grill me on the release plan".

### Klartext (Plain Talk)

Text written with AI help gives itself away: "It's not X, it's Y", "Here's the kicker", "No setup. No cost. Just results.", buzzwords, a recap nobody asked for. Klartext removes those habits and keeps your meaning, your voice and your jokes.

- Three jobs: **edit** (default), **audit** (list problems without rewriting), **draft** (write new text in your voice)
- A real German pattern library, not a translation: nominal style, «nahtlos», «Mehrwert», «Tauchen wir ein», chatbot residue
- Knows text types: store listings, READMEs, job applications, posts and UI texts each get their own rules
- Respects Swiss spelling (ss, «…») and your du/Sie choice
- Never invents facts and never claims to detect AI authorship

**Start it** with something like: "Klartext this store description" or "Does this README sound like AI?"

### Drehbuch (Screenplay)

Scrolling becomes the timeline. Drehbuch plans a landing page like a short film (acts, a feeling curve, one peak, a real ending), builds it on its own small scroll engine and checks it by photographing every scroll position on desktop, phone and with reduced motion.

- Short brief, then a screenplay table: one device per act, at least four device families, never the same twice in a row
- One bespoke signature move per page, written in page code
- Delivered as **one self-contained HTML file** (engine inlined), ready for an artifact, itch.io or GitHub Pages
- Phone-first composition and a design floor with a refuse list (no "scroll down" arrows, no fake stats, no AI-purple gradients)
- Example: [`drehbuch/examples/antarium`](drehbuch/examples/antarium) – scrolling digs you down through the earth into an ant nest

**Start it** with something like: "Drehbuch a landing page for my game" or "Make a scroll page for my app".

### Beweispflicht (Burden of Proof)

"Works now!" costs nothing to write and a lot when it is wrong. Beweispflicht makes the agent prove a claim before it makes it: run the test, open the file, render the page, recalculate the number. When a proof is out of reach (your phone, a store review), you get a short test to do yourself instead of a confident guess.

- A proof table for code, web apps and PWAs, games, Android builds, deploys, files, numbers, research and skills
- Works without a terminal too: chat-only work is labeled honestly as inspected, not verified
- Five clear status words, from "Done" to "Blocked", and short reports that fit a phone screen
- An adversarial review round for risky claims (security, money, data loss)
- No scripts at all

**Start it** by just building something, or ask: "Did you actually test that?"

### Schleuse (Airlock)

Skills and plugins run with your permissions. In early 2026, a security study of almost 4,000 public skills found critical problems (malware, prompt injection, exposed secrets) in more than one in ten. Schleuse checks a candidate before it gets near your setup: origin, license, a static scan, reading the flagged lines in context, value for your collection, and a clear verdict from 🟢 adopt to 🔴 keep out.

- Bundled scanner: standard library only, no network, never executes or imports what it scans
- Finds hidden instructions (invisible Unicode, look-alike letters, encoded payloads), remote code, key theft, webhooks, auto-running hooks and config files that silently grant broad access
- "Not checked is never clean": unreadable files block a green verdict
- Also checks your own build or APK for leaked API keys, and masks any key it finds so it never lands in the chat
- Phone route: download a repo as ZIP on GitHub and attach it to the chat

**Start it** with something like: "Schleuse this skill" plus a GitHub link, or "Is this plugin safe?"

### Bauplan (Build Plan)

Big changes fail in the middle. Bauplan cuts the work into small steps that each end with a running app and a proof, then builds them one by one.

- Every step names the files, how to prove it (a command, or a test you can do on your phone) and how to undo it
- Ticks only with real evidence; untested steps stay open
- Saved data and save games are protected: version, migration, backup first
- Stop rule: when a step fails twice or grows too big, it replans instead of pushing on
- A short plan for small jobs, so it never feels heavy

**Start it** with something like: "Make a Bauplan for the statistics feature" or "How do we approach this?"

### Stilkompass (Style Compass)

AI-built screens tend to look alike: indigo gradient, glass cards, three feature boxes. Stilkompass picks a direction that fits your users and their moment (outdoors mid-workout, at night, at a desk) and turns it into a small set of design tokens.

- Eleven style directions with their trade-offs, plus rules for health, finance, fitness, kids, games and landing pages
- Bundled contrast script: WCAG ratios for light and dark mode and a color-blindness estimate for pairs like gains and losses
- Free fonts and icon sets only, web fonts self-hosted
- Saves the result in your project, so the next chat keeps the same look

**Start it** with something like: "Stilkompass for my trading app" or "Which style fits my game?"

### Working together

The skills work alone, and they fit together: Kreuzfeuer clears the idea, Bauplan plans the build, Stilkompass sets the look, Beweispflicht guards every "done", and Schleuse checks anything foreign before it comes in.

### Install

**claude.ai (web, desktop, mobile):** Download a skill folder (for example `kreuzfeuer` or `klartext`) as a ZIP and upload it under Settings → Capabilities → Skills. (Menu names can change; look for "Skills".)

**Claude Code:** Copy the folders into your skills directory:

```bash
git clone https://github.com/ui-edi/skills.git
cp -r skills/kreuzfeuer skills/klartext skills/drehbuch skills/beweispflicht skills/schleuse skills/bauplan skills/stilkompass ~/.claude/skills/
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
- Endet mit dem kleinsten ersten Schritt, den man schon testen kann, und einer sortierten Übergabe-Liste, jede Aufgabe mit «fertig, wenn…»

**Starten** zum Beispiel mit: «Nimm meine App-Idee ins Kreuzfeuer» oder «Grill mich zum Release-Plan».

### Klartext

KI-Texte verraten sich: «Es geht nicht um X, sondern um Y», «Und jetzt kommt der Clou», «Kein Stress. Kein Aufwand. Einfach Ergebnisse.», Buzzwords und ein Fazit, das keiner bestellt hat. Klartext entfernt diese Muster und behält deine Aussage, deine Stimme und deinen Humor.

- Drei Aufgaben: **überarbeiten** (Standard), **prüfen** (Probleme auflisten, ohne umzuschreiben), **schreiben** (neuer Text in deiner Stimme)
- Eine echte deutsche Muster-Sammlung, keine Übersetzung: Nominalstil, «nahtlos», «Mehrwert», «Tauchen wir ein», Chatbot-Reste
- Kennt Textarten: Store-Einträge, READMEs, Bewerbungen, Posts und App-Texte haben eigene Regeln
- Respektiert Schweizer Schreibweise (ss, «…») und deine Du/Sie-Wahl
- Erfindet nie Fakten und behauptet nie, KI-Texte zu erkennen

**Starten** zum Beispiel mit: «Mach Klartext aus dieser Store-Beschreibung» oder «Klingt dieses README nach KI?»

### Drehbuch

Scrollen wird zur Zeitleiste. Drehbuch plant eine Landingpage wie einen Kurzfilm (Akte, Gefühlskurve, ein Höhepunkt, ein echter Schluss), baut sie mit einer eigenen kleinen Scroll-Engine und prüft sie, indem es jede Scroll-Position auf Desktop, Handy und mit reduzierter Bewegung fotografiert.

- Kurzes Briefing, dann eine Drehbuch-Tabelle: ein Effekt pro Akt, mindestens vier verschiedene, nie zweimal derselbe hintereinander
- Pro Seite ein eigener Signature-Effekt, direkt im Seitencode
- Ergebnis ist **eine einzige HTML-Datei** (Engine eingebaut), bereit für ein Artefakt, itch.io oder GitHub Pages
- Handy zuerst gestaltet, mit Design-Grundregeln und Verbotsliste (keine «Scroll down»-Pfeile, keine erfundenen Zahlen, keine KI-Lila-Verläufe)
- Beispiel: [`drehbuch/examples/antarium`](drehbuch/examples/antarium) – beim Scrollen gräbst du dich durch die Erde ins Ameisennest

**Starten** zum Beispiel mit: «Schreib ein Drehbuch für eine Landingpage meines Games» oder «Mach eine Scroll-Seite für meine App».

### Beweispflicht

«Läuft jetzt!» ist schnell geschrieben und teuer, wenn es nicht stimmt. Beweispflicht lässt den Agenten erst beweisen und dann behaupten: Test laufen lassen, Datei öffnen, Seite rendern, Zahl nachrechnen. Wo kein Beweis möglich ist (dein Handy, eine Store-Prüfung), bekommst du einen kurzen Test zum Selbermachen statt einer selbstsicheren Vermutung.

- Eine Beweistabelle für Code, Web-Apps und PWAs, Games, Android-Builds, Deploys, Dateien, Zahlen, Recherche und Skills
- Funktioniert auch ohne Terminal: Reine Chat-Arbeit wird ehrlich als «geprüft», nicht als «gesehen» markiert
- Fünf klare Status-Wörter von «Fertig» bis «Blockiert» und kurze Berichte, die auf einen Handy-Bildschirm passen
- Eine Zweifelsrunde für riskante Aussagen (Sicherheit, Geld, Datenverlust)
- Ganz ohne Skripte

**Starten** einfach, indem du etwas bauen lässt, oder fragen: «Hast du das wirklich getestet?»

### Schleuse

Skills und Plugins laufen mit deinen Rechten. Anfang 2026 fand eine Sicherheitsstudie in fast 4000 öffentlichen Skills bei mehr als jedem zehnten kritische Probleme (Malware, Prompt Injection, offengelegte Schlüssel). Die Schleuse prüft einen Kandidaten, bevor er in die Nähe deines Setups kommt: Herkunft, Lizenz, statischer Scan, Lesen der markierten Stellen im Kontext, Nutzen für deine Sammlung und ein klares Urteil von 🟢 übernehmen bis 🔴 Finger weg.

- Mitgelieferter Scanner: nur Standardbibliothek, kein Netzwerk, führt nie aus oder importiert, was er prüft
- Findet versteckte Anweisungen (unsichtbare Zeichen, Doppelgänger-Buchstaben, kodierte Inhalte), Fremdcode aus dem Netz, Schlüsseldiebstahl, Webhooks, Autostart-Hooks und Konfigurationen, die still weitreichende Rechte geben
- «Nicht geprüft ist nie sauber»: Unlesbare Dateien verhindern ein grünes Urteil
- Prüft auch deinen eigenen Build oder deine APK auf geleakte API-Keys und zeigt Funde nur maskiert, damit nie ein Key im Chat landet
- Weg am Handy: Repo auf GitHub als ZIP herunterladen und an den Chat anhängen

**Starten** zum Beispiel mit: «Schick diesen Skill durch die Schleuse» plus GitHub-Link, oder «Ist dieses Plugin sicher?»

### Bauplan

Grosse Änderungen scheitern in der Mitte. Der Bauplan zerlegt die Arbeit in kleine Schritte, nach denen die App jeweils läuft und bewiesen ist, und baut sie dann einzeln.

- Jeder Schritt nennt die Dateien, den Beweis (ein Befehl oder ein Test, den du am Handy machst) und den Weg zurück
- Abgehakt wird nur mit echtem Beweis; ungetestete Schritte bleiben offen
- Gespeicherte Daten und Spielstände sind geschützt: Version, Migration, zuerst ein Backup
- Abbruchregel: Scheitert ein Schritt zweimal oder wird er zu gross, wird neu geplant statt weitergedrückt
- Ein Kurzplan für kleine Aufgaben, damit es nie schwerfällig wird

**Starten** zum Beispiel mit: «Mach einen Bauplan für die Statistik-Funktion» oder «Wie gehen wir das an?»

### Stilkompass

KI-gebaute Oberflächen sehen sich oft ähnlich: Indigo-Verlauf, Glas-Karten, drei Feature-Kästen. Der Stilkompass wählt eine Richtung, die zu deinen Nutzern und ihrem Moment passt (draussen im Training, nachts, am Schreibtisch), und macht daraus ein kleines Set an Design-Tokens.

- Elf Stil-Richtungen mit ihren Vor- und Nachteilen, dazu Regeln für Gesundheit, Finanzen, Fitness, Kinder, Games und Landingpages
- Mitgeliefertes Kontrast-Skript: WCAG-Werte für Hell- und Dunkelmodus und eine Farbenblindheits-Schätzung für Paare wie Gewinn und Verlust
- Nur freie Schriften und Icon-Sets, Webfonts selbst gehostet
- Speichert das Ergebnis im Projekt, damit der nächste Chat denselben Look behält

**Starten** zum Beispiel mit: «Stilkompass für meine Trading-App» oder «Welcher Stil passt zu meinem Game?»

### Zusammenspiel

Jeder Skill funktioniert allein, und zusammen greifen sie ineinander: Kreuzfeuer klärt die Idee, der Bauplan plant den Bau, der Stilkompass legt den Look fest, die Beweispflicht bewacht jedes «fertig», und die Schleuse prüft alles Fremde, bevor es hereinkommt.

### Installation

**claude.ai (Web, Desktop, Handy):** Einen Skill-Ordner (z. B. `kreuzfeuer` oder `klartext`) als ZIP herunterladen und unter Einstellungen → Fähigkeiten → Skills hochladen. (Menünamen können sich ändern; such nach «Skills».)

**Claude Code:** Ordner in dein Skills-Verzeichnis kopieren:

```bash
git clone https://github.com/ui-edi/skills.git
cp -r skills/kreuzfeuer skills/klartext skills/drehbuch skills/beweispflicht skills/schleuse skills/bauplan skills/stilkompass ~/.claude/skills/
```

**Andere Agenten:** Den Agenten auf die `SKILL.md` des Skills verweisen.

---

## Credits

Kreuzfeuer is inspired by the idea behind "grill-me" from [AIS-OS](https://github.com/nateherkai/AIS-OS) by Nate Herk (MIT). The text is written independently.
Kreuzfeuer ist von der Idee hinter «grill-me» aus [AIS-OS](https://github.com/nateherkai/AIS-OS) von Nate Herk (MIT) inspiriert. Der Text ist eigenständig geschrieben.

Klartext is inspired by [human-speak](https://github.com/nateherkai/human-speak) by Nate Herk (MIT). The text is written independently and extended with German patterns.
Klartext ist von [human-speak](https://github.com/nateherkai/human-speak) von Nate Herk (MIT) inspiriert. Der Text ist eigenständig geschrieben und um deutsche Muster erweitert.

Drehbuch is inspired by [scroll-craft](https://github.com/nateherkai/scroll-craft) by Nate Herk (MIT). Text, engine and scripts are written independently.
Drehbuch ist von [scroll-craft](https://github.com/nateherkai/scroll-craft) von Nate Herk (MIT) inspiriert. Text, Engine und Skripte sind eigenständig geschrieben.

Beweispflicht is inspired by "verification-before-completion" from [Superpowers](https://github.com/obra/superpowers) by Jesse Vincent (MIT) and "doubt-driven-development" from [Agent Skills](https://github.com/addyosmani/agent-skills) by Addy Osmani (MIT). Written independently; see [NOTICE](beweispflicht/NOTICE).
Beweispflicht ist von «verification-before-completion» aus [Superpowers](https://github.com/obra/superpowers) von Jesse Vincent (MIT) und «doubt-driven-development» aus [Agent Skills](https://github.com/addyosmani/agent-skills) von Addy Osmani (MIT) inspiriert. Eigenständig geschrieben; siehe [NOTICE](beweispflicht/NOTICE).

Schleuse is original work, informed by Snyk's ToxicSkills study (2026), the "unassessable is never clean" principle of [Trail of Bits](https://github.com/trailofbits/skills) and the regex-only approach of clawhub-bridge. No text or code was copied.
Schleuse ist eine eigene Arbeit, angeregt durch Snyks ToxicSkills-Studie (2026), den Grundsatz «nicht prüfbar ist nie sauber» von [Trail of Bits](https://github.com/trailofbits/skills) und den reinen Regex-Ansatz von clawhub-bridge. Kein Text und kein Code wurde übernommen.

Bauplan is inspired by "writing-plans" from [Superpowers](https://github.com/obra/superpowers) (MIT) and "planning-and-task-breakdown" from [Agent Skills](https://github.com/addyosmani/agent-skills) (MIT). Written independently; see [NOTICE](bauplan/NOTICE).
Bauplan ist von «writing-plans» aus [Superpowers](https://github.com/obra/superpowers) (MIT) und «planning-and-task-breakdown» aus [Agent Skills](https://github.com/addyosmani/agent-skills) (MIT) inspiriert. Eigenständig geschrieben; siehe [NOTICE](bauplan/NOTICE).

Stilkompass is inspired by the product-to-style idea of [UI UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) by Next Level Builder (MIT). No data was copied; see [NOTICE](stilkompass/NOTICE).
Stilkompass ist von der Idee «vom Produkt zum Stil» aus [UI UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) von Next Level Builder (MIT) inspiriert. Keine Daten übernommen; siehe [NOTICE](stilkompass/NOTICE).

## License

MIT, see [LICENSE](LICENSE).
