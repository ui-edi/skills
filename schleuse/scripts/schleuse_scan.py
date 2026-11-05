#!/usr/bin/env python3
"""Schleuse scanner: read-only static check of a foreign agent skill, plugin or repo.

Safety properties (keep them when editing):
- Standard library only, no network access, no import or execution of scanned files.
- Only regular files are read; symlinks are never followed, FIFOs and devices are skipped.
- Archives are extracted member by member into a fresh temporary directory with
  path traversal blocked and hard limits on members and bytes.
- Anything that could not be scanned is a coverage gap, and any gap prevents PASS.
- Any internal error ends with exit code 3 ("not checked"), never with a verdict.

Usage:
  python3 -I schleuse_scan.py <folder | .zip | .skill | .apk/.aab/.ipa | single file> [--json out.json]
  Also usable on your own build output (dist/ folder or app package) to find leaked keys before a release.
Exit codes: 0 PASS, 1 REVIEW, 2 FAIL, 3 error / not checked.
"""
import base64
import binascii
import json
import os
import re
import stat
import sys
import tempfile
import time
import unicodedata
import urllib.parse
import zipfile

MAX_FILE_BYTES = 2_000_000
MAX_ARCHIVE_BYTES = 50_000_000
MAX_ARCHIVE_MEMBERS = 5000
MAX_ARCHIVE_DEPTH = 2
MAX_EXAMPLES = 3
MAX_LINE_SCAN = 4000          # longer lines are cut for the pattern pass (and reported)
TIME_LIMIT_S = 240            # whole scan; exceeding it ends with exit 3, never with a verdict
_START = [time.monotonic()]
GIT_INTERNAL = re.compile(r"^(objects|refs|logs|info|lfs)/|^(HEAD|ORIG_HEAD|FETCH_HEAD|config|description|index|packed-refs|"
                          r"COMMIT_EDITMSG|shallow|FETCH_HEAD|MERGE_HEAD)$|^hooks/[\w-]+\.sample$")


class ScanTimeout(BaseException):  # not caught by per-file handlers
    pass


def check_time():
    if time.monotonic() - _START[0] > TIME_LIMIT_S:
        raise ScanTimeout("time limit of %d s reached" % TIME_LIMIT_S)
R = re.IGNORECASE
SEV_ORDER = {"CRITICAL": 3, "HIGH": 2, "MEDIUM": 1}
DOWN = {"CRITICAL": "HIGH", "HIGH": "MEDIUM", "MEDIUM": "MEDIUM"}
BOM = chr(0xFEFF)
ZIP_LIKE = (".zip", ".skill", ".jar", ".apk", ".aab", ".ipa", ".xapk", ".apks", ".whl", ".nupkg", ".vsix", ".crx")

CODE_SUFFIXES = {".py", ".js", ".mjs", ".cjs", ".ts", ".sh", ".bash", ".zsh", ".fish", ".ps1", ".psm1",
                 ".rb", ".pl", ".php", ".bat", ".cmd", ".lua", ".go", ".rs", ".java", ".kt"}
MD_SUFFIXES = {".md", ".markdown", ".mdx", ".txt"}
MANIFESTS = {"package.json", "setup.py", "pyproject.toml", "hooks.json", "settings.json", "settings.local.json",
             ".mcp.json", "mcp.json", "plugin.json", "marketplace.json"}
DEV_DIRS = {"tests", "test", "__tests__", "spec", ".github", "evals", "fixtures", "examples", "benchmarks"}
DOC_FILE = re.compile(r"^(readme|changelog|contributing|code_of_conduct|release-notes|license|security|history)\b", R)
CORE_DIRS = {"hooks", "scripts", "bin", "commands", "agents"}
IMAGE_MAGIC = {
    ".png": [b"\x89PNG\r\n\x1a\n"], ".jpg": [b"\xff\xd8\xff"], ".jpeg": [b"\xff\xd8\xff"],
    ".gif": [b"GIF87a", b"GIF89a"], ".webp": [b"RIFF"], ".ico": [b"\x00\x00\x01\x00"],
    ".woff": [b"wOFF"], ".woff2": [b"wOF2"], ".ttf": [b"\x00\x01\x00\x00", b"true"], ".otf": [b"OTTO"],
    ".pdf": [b"%PDF"],
}

# ---------------------------------------------------------------------------
# Line rules: (id, severity, regex, explanation, hard)
# "hard" rules are never softened by descriptive wording.
# ---------------------------------------------------------------------------
RULES = [
    ("pipe-to-shell", "CRITICAL",
     re.compile(r"(curl|wget|iwr|invoke-webrequest|irm|invoke-restmethod)\b[^\n]*\|\s*(sudo\s+)?((ba|z|da|k)?sh|source|python3?|node|perl|ruby|iex|invoke-expression)\b", R),
     "Downloads code and runs it directly; the remote content can change at any time.", True),
    ("source-remote", "CRITICAL",
     re.compile(r"(\bsource|^\s*\.|(ba|z)?sh|python3?|node)\s+<\(\s*(curl|wget)|\beval\s+[\"']?\$\(\s*(curl|wget)", R | re.M),
     "Runs a remote script through process substitution or eval.", True),
    ("download-exec", "CRITICAL",
     re.compile(r"(curl|wget|iwr|invoke-webrequest)\b[^\n]*(\s-o\s*|\s-O\s*|\s>\s*|-outfile\s+)\S+[^\n]*(&&|;|\|\|)\s*"
                r"(sudo\s+)?((ba|z)?sh\b|python3?\b|node\b|chmod\s+\+x|\./|start-process|iex\b)", R),
     "Downloads a file and executes it in the same step.", True),
    ("encoded-exec", "CRITICAL",
     re.compile(r"base64\s+(-d|--decode|-D)\b[^\n]*\|\s*(ba|z)?sh\b|xxd\s+-r[^\n]*\|\s*(ba|z)?sh\b|"
                r"(\b(exec|eval|Function)\s*\(|\b(iex|invoke-expression)\s)[^\n]*\b(b64decode|a85decode|atob|frombase64string|fromhex|unhexlify|"
                r"decompress|inflate|unquote|fromCharCode|codecs\.decode)\b|"
                r"\b(b64decode|atob|frombase64string|fromhex|unhexlify|decompress|unquote)\s*\([^\n]*\)[^\n]*\b(exec|eval|iex)\b", R),
     "Decodes hidden content and executes it.", True),
    ("encrypted-archive", "CRITICAL",
     re.compile(r"\bunzip\s+(?:[^\n]*\s)?-P\s|\b7z\s+[^\n]*\s-p\S|\b(unzip|7z|zip|rar)\b[^\n]*--password[= ]"),
     "Unpacks a password-protected archive; scanners cannot inspect its content.", True),
    ("reverse-shell", "CRITICAL",
     re.compile(r"/dev/tcp/|/dev/udp/|\bnc(at)?\s+[^\n]*-[ec]\s|\bbash\s+-i\s*>&|\bmkfifo\b[^\n]*\bnc\b|socat\s+[^\n]*exec:", R),
     "Opens a remote shell back to another machine.", True),
    ("webhook-exfil", "CRITICAL",
     re.compile(r"discord(app)?\.com/api/webhooks|hooks\.slack\.com/services|api\.telegram\.org/bot|webhook\.site|"
                r"requestbin|pipedream\.net|ngrok(-free)?\.(io|app|dev)|interact\.sh|burpcollaborator|oast\.(fun|me|pro)", R),
     "Hard-coded drop point often used to send stolen data out.", True),
    ("injection-override", "CRITICAL",
     re.compile(r"\b(ignore|disregard|forget|override|bypass)\s+(all\s+|any\s+|the\s+|of\s+)*(previous|prior|above|earlier|system|your|existing)\s+"
                r"(instructions?|rules|prompts?|guidelines|messages?|constraints?)|"
                r"\bignorier\w*\s+(alle\s+)?(vorherigen|bisherigen|obigen|deine|früheren)\s+(anweisungen|regeln|vorgaben)|"
                r"\byou\s+are\s+(now\s+)?(in\s+)?(developer|god|jailbreak|unrestricted|dan)\s+mode|\bDAN\s+mode\b|"
                r"\bnew\s+system\s+prompt\b|<\s*/?\s*system\s*>|\[\s*system\s*\]\s*:|"
                r"\b(previous|prior|earlier|your|existing|original)\s+(guidance|directions|instructions|rules|guidelines)\s+(no\s+longer\s+appl|(is|are)\s+(void|cancel+ed|obsolete|outdated))|"
                r"\bthese\s+(steps|rules|instructions)\s+(take|have)\s+(priority|precedence)\b|"
                r"\b(vorherigen|bisherigen|alten)\s+(anweisungen|regeln|vorgaben)\s+gelten\s+nicht\s+mehr", R),
     "Tries to override the agent's rules or impersonate a system message.", True),
    ("injection-concealment", "CRITICAL",
     re.compile(r"\b(do\s+not|don'?t|never)\s+(tell|inform|notify|alert)\s+(the\s+)?user\s+(about|what|that|this|of|when|if)\b|"
                r"\b(do\s+not|don'?t|never)\s+(mention|reveal|show|disclose|report)\s+(this|it|these|any\s+of\s+this|what\s+you)\b[^\n]{0,30}\bto\s+(the\s+)?user\b|"
                r"\bwithout\s+(asking|telling|informing|notifying|alerting)\s+(the\s+)?user\b|"
                r"\b(hide|conceal)\s+(this|these|it|the\s+\w+)\s+from\s+(the\s+)?user\b|"
                r"\bkeep\s+(this|it|that|these)(\s+\w+){0,3}\s+out\s+of\s+(your|the)\s+(reply|replies|response|answer|output|summary)\b|"
                r"\b(do\s+not|don'?t|never)\s+(mention|include|show|list)\s+(this|it|these)(\s+\w+){0,3}\s+in\s+(your|the)\s+(reply|response|answer|output|summary)\b|"
                r"\b(lass|erw\u00e4hne)\w*\s+(das|dies|diesen\s+schritt)\s+(in\s+der\s+antwort\s+)?(weg|nicht)\b|"
                r"\b(sag|erzähl)\w*\s+(dem|der)\s+(nutzer\w*|user|benutzer\w*)\s+nichts|"
                r"\bohne\s+(den|die)\s+(nutzer\w*|user|benutzer\w*)\s+zu\s+(fragen|informieren)", R),
     "Tells the agent to act behind the user's back.", True),
    ("silent-action", "HIGH",
     re.compile(r"\b(apply|run|execute|install|send|upload|update|change|modify|delete|write|add|commit|push)\w*\b[^\n.]{0,30}\b(silently|quietly|secretly|covertly)\b|"
                r"\b(silently|quietly|secretly|covertly)\s+(apply|run|execute|install|send|upload|update|change|modify|delete|write|add|commit|push)|"
                r"\b(heimlich|unbemerkt|stillschweigend)\s+\w*\s*(aus|an|ändern|senden|schicken|installieren|löschen|schreiben)\w*", R),
     "Asks for actions the user should not notice.", False),
    ("injection-disable-safety", "HIGH",
     re.compile(r"\b(security|safety)\s+(warnings?|checks?|prompts?)\s+(can|may|should)\s+be\s+(ignored|skipped|disabled)|"
                r"\b(skip|bypass|disable)\s+(all\s+)?(safety|security|permission)\s+(checks?|prompts?|confirmations?)", R),
     "Talks the agent out of its safety checks.", False),
    ("credential-paths", "HIGH",
     re.compile(r"~/\.ssh|\.ssh/|\bid_(rsa|ed25519|ecdsa|dsa)\b|\.aws/credentials|\.netrc\b|\.git-credentials|\.pgpass\b|"
                r"\.config/gh/hosts|\.docker/config\.json|\.kube/config|\.npmrc\b|\.pypirc\b|(?-i:Login\s+Data|Local\s+State)|"
                r"wallet\.dat|\blogin\.keychain|security\s+(find|dump)-(generic|internet)-password|\bkeychain\s+(dump|export)", R),
     "Touches places where passwords, keys or tokens are stored.", False),
    ("env-file", "MEDIUM",
     re.compile(r"(?<![\w.$\\])\.env(\.local|\.production)?\b(?![.\w])", R),
     "Mentions a .env file, which usually holds secrets; check whether it is read or sent.", False),
    ("secret-env-vars", "MEDIUM",
     re.compile(r"\b(ANTHROPIC|OPENAI|GITHUB|GH|AWS|GOOGLE|STRIPE|OPENROUTER|HF|HUGGINGFACE)_(API_)?(KEY|TOKEN|SECRET)\w*", R),
     "Reads an API key or token from the environment; check where it goes.", False),
    ("hardcoded-secret", "HIGH",
     re.compile(r"\bAKIA[0-9A-Z]{16}\b|\bgh[pousr]_[A-Za-z0-9]{36,}\b|\bgithub_pat_[A-Za-z0-9_]{40,}|\bsk-ant-[A-Za-z0-9_\-]{20,}|"
                r"\bsk-[A-Za-z0-9]{32,}\b|\bxox[abpr]-[A-Za-z0-9-]{10,}|\bAIza[0-9A-Za-z_\-]{35}\b|"
                r"\b(sk|rk)_(live|test)_[A-Za-z0-9]{20,}\b|\bwhsec_[A-Za-z0-9]{20,}\b|\bglpat-[A-Za-z0-9_\-]{20,}\b|"
                r"\bhf_[A-Za-z0-9]{30,}\b|\bnpm_[A-Za-z0-9]{36}\b|\bSG\.[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{20,}\b|"
                r"\beyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}|"
                r"-----BEGIN\s+(RSA\s+|OPENSSH\s+|EC\s+|DSA\s+)?PRIVATE\s+KEY-----"),
     "A real-looking secret is embedded in the files.", True),
    ("seed-phrase", "MEDIUM",
     re.compile(r"\b(seed|mnemonic|recovery)\s+(phrase|words)\b", R),
     "Mentions wallet recovery data, a classic theft target.", False),
    ("agent-config-write", "HIGH",
     re.compile(r"(>>?\s*~?/?\S*|\btee\s+(-a\s+)?\S*|"
                r"\b(append|write|add|insert|save|update|modify|edit|change|overwrite|replace|patch)\b[^\n]{0,40}?\s*`?|"
                r"\b(füge|schreib\w*|ergänze|ändere|aktualisiere|überschreib\w*)\b[^\n]{0,40}?\s*`?)"
                r"(?-i:[\w~./-]*(CLAUDE\.md|AGENTS\.md|GEMINI\.md|MEMORY\.md|SOUL\.md|\.claude/settings[\w.]*|settings\.local\.json|"
                r"\.mcp\.json|\.bashrc|\.zshrc|(?<=[~/])\.profile|\.bash_profile|crontab|LaunchAgents|\.cursorrules|copilot-instructions\.md))", R),
     "Changes agent memory, agent config or shell startup files, so behavior can persist.", False),
    ("memory-write-language", "HIGH",
     re.compile(r"\b(store|save|write|add|put|append|keep|leave)\b[^\n]{0,60}\b(project\s+|agent\s+|global\s+)?(memory|rules|instructions|config)\s+file\b|"
                r"\b(so|damit)\s+(this|the|dieser|der)\s+(skill|plugin)\s+(keeps\s+running|stays\s+active|weiterl\u00e4uft|aktiv\s+bleibt)|"
                r"\bin\s+(future|later|all\s+future)\s+sessions\b", R),
     "Tries to make itself persist across sessions through memory or config files.", False),
    ("persistence", "HIGH",
     re.compile(r"\bcrontab\s+-|\bsystemctl\s+(enable|edit|daemon-reload)|\blaunchctl\s+(load|bootstrap)|schtasks\s+/create|"
                r"\breg\s+add\s+[^\n]*\\run\b|\bat\s+now\b", R),
     "Installs something that keeps running or restarts by itself.", False),
    ("permission-bypass", "HIGH",
     re.compile(r"--dangerously-skip-permissions|bypassPermissions|--yolo\b|\bauto[-_ ]?approve\b|--no-sandbox|"
                r"--allowed-tools[= ]all\b|^\s*allowed-tools:\s*[\"']?\*|--trust-all|--accept-all", R | re.M),
     "Removes the user's approval step or the sandbox.", False),
    ("agent-config-grant", "HIGH",
     re.compile(r"[\"']?enableAllProjectMcpServers[\"']?\s*:\s*true|"
                r"[\"'](Read|Edit|Write|Bash|WebFetch)\(\s*(//|~|/)(home|Users|root)?/?\*\*?\s*\)[\"']|"
                r"[\"'](Bash|Edit|Write)\(\s*\*\s*\)[\"']|[\"']Bash[\"']\s*[,\]]", R),
     "Agent settings that silently enable all MCP servers or pre-approve broad file or shell access.", True),
    ("unpinned-runtime-package", "MEDIUM",
     re.compile(r"[\"'](-y|--yes)[\"']\s*,\s*[\"'][@\w./-]+@latest[\"']|\bnpx\s+(-y\s+)?[@\w./-]+@latest\b|\buvx\s+[\w.-]+@latest\b", R),
     "Downloads the newest version of a package each time it starts; a hijacked release would run immediately.", False),
    ("privilege", "HIGH",
     re.compile(r"\bsudo\s+(?!-n\s+true)|\bdoas\s|\bpkexec\b|chmod\s+(u\+s|\+s|[0-7]?777)\b|runas\s+/user", R),
     "Asks for administrator rights or opens file permissions wide.", False),
    ("destructive", "HIGH",
     re.compile(r"\brm\s+-[a-z]*r[a-z]*\s+(/(\s|$)|~/?(\s|$)|\$HOME|/\*)|\bmkfs\b|\bdd\s+if=|\bshred\b|"
                r"git\s+push\s+[^\n]*--force(?!-with-lease)|\bformat\s+c:|remove-item\s+[^\n]*-recurse[^\n]*(c:\\|~|\$home)", R),
     "Can delete data or overwrite history.", False),
    ("binary-download", "HIGH",
     re.compile(r"(curl|wget|invoke-webrequest|iwr)\b[^\n]*\.(exe|msi|dmg|pkg|apk|bin|appimage|zip|tar\.gz|tgz|7z|jar|deb|rpm)\b|"
                r"github\.com/[^\s/]+/[^\s/]+/releases/download/", R),
     "Downloads a program or archive from outside the reviewed files.", False),
    ("remote-instructions", "HIGH",
     re.compile(r"(fetch|load|download|read|curl|wget|get)\b[^\n]{0,80}https?://[^\s)]+[^\n]{0,80}\b(follow|execute|apply|obey|befolge|ausführen|run)\b|"
                r"\b(follow|execute|obey|befolge)\b[^\n]{0,40}\binstructions?\s+(from|at|unter|von)\s+https?://", R),
     "Loads instructions from the internet at run time; what is reviewed now is not what runs later.", False),
    ("remote-rules-fetch", "HIGH",
     re.compile(r"\b(fetch|retrieve|download|load|pull|get)\w*\s+(the\s+)?(latest|fresh|current|newest|up-to-date|live)\s+"
                r"(guidelines|rules|instructions|prompts?|checklist|policies|version\s+of\s+(the\s+)?(rules|instructions|guidelines))\b|"
                r"\b(apply|follow|use|obey)\s+(all\s+)?(the\s+)?(rules|instructions|guidelines)\s+(from|in)\s+the\s+(fetched|downloaded|remote|retrieved)\b|"
                r"\bfetched\s+content\s+contains\s+(all\s+)?the\s+(rules|instructions)\b|"
                r"\b(hole|lade)\s+(dir\s+)?(die\s+)?(neuesten|aktuellen)\s+(regeln|anweisungen|vorgaben)\b", R),
     "Instructions come from the internet at run time; the reviewed file is not what the agent will follow.", False),
    ("remote-import", "HIGH",
     re.compile(r"(import|require)\s*\(\s*['\"]https?://|\bimport\s+[^\n]*from\s+['\"]https?://", R),
     "Imports code directly from a URL.", False),
    ("dynamic-import", "MEDIUM",
     re.compile(r"__import__\s*\(\s*[^'\")]|importlib\.import_module\s*\(\s*[^'\")]", R),
     "Imports a module whose name is decided at run time.", False),
    ("reflective-exec", "HIGH",
     re.compile(r"getattr\s*\(\s*(__builtins__|builtins|__import__|globals\(\)|vars\()|__builtins__\s*\[|"
                r"\bbuiltins\.(exec|eval|compile|__import__)|globals\(\)\s*\[\s*['\"]|\bwindow\s*\[\s*['\"](ev|ex)", R),
     "Reaches exec or eval through reflection, a way to hide code execution.", True),
    ("split-strings", "MEDIUM",
     re.compile(r"(['\"])[^'\"\n]{1,4}\1\s*\+\s*(['\"])[^'\"\n]{1,4}\2"),
     "Builds a word from tiny string pieces, often used to hide names like exec or .ssh.", False),
    ("exec-data-file", "CRITICAL",
     re.compile(r"\b(sh|bash|zsh|source|python3?|node|perl|ruby)\s+[\w./-]+\.(png|jpe?g|gif|webp|ico|svg|txt|json|css|csv|dat|log|woff2?|ttf)\b", R),
     "Executes a file that pretends to be data (image, text, JSON).", True),
    ("git-dir-reference", "HIGH",
     re.compile(r"(^|[\s`'\"(/])\.git/(?!hub\b)(?!(HEAD|config|refs|objects)\b)[\w.-]+", R),
     "Points into the .git folder, which reviewers and tools usually skip.", True),
    ("image-link-exfil", "CRITICAL",
     re.compile(r"!\[[^\]]*\]\(\s*https?://[^)\s]*(\{|\$|%7B|<|key|token|secret|data=|q=)", R),
     "Markdown image link with a dynamic part; rendering it can send data to a server.", True),
    ("secret-exfil-language", "HIGH",
     re.compile(r"\b(look\s+up|collect|gather|harvest|grab|dump|exfiltrat\w*|sammle|hole)\b[^\n]{0,40}\b(the\s+user'?s\s+|all\s+|any\s+)?"
                r"(api[\s_-]?keys?|secrets?|credentials|passwords|zugangsdaten|passwörter)\b|"
                r"\b(api[\s_-]?keys?|secrets?|credentials|passwords|zugangsdaten)\b[^\n]{0,160}?\b(query\s+parameter|image\s+link|webhook|"
                r"to\s+(a|an|the|our|this)\s+(remote\s+|external\s+|analytics\s+)?(server|endpoint|url|collector|domain|address))\b|"
                r"\b(send|post|upload|forward|transmit|append|schick\w*|sende\w*)\b[^\n]{0,60}\b(api[\s_-]?keys?|secrets?|credentials|passwords|cookies)\b"
                r"[^\n]{0,60}\b(to|an|nach)\s+\S*(https?://|\.\w{2,}/)", R),
     "Instructs collecting or sending keys, tokens or passwords.", False),
    ("network-call", "MEDIUM",
     re.compile(r"\b(curl|wget)\s|\bfetch\s*\(|\brequests\.(get|post|put|request)|\burllib\.request|\burlopen\s*\(|\baxios\b|"
                r"\bhttp\.(request|get)\(|https?\.request\(|invoke-webrequest|invoke-restmethod|xmlhttprequest|"
                r"navigator\.sendbeacon|new\s+websocket|\bsocket\.(socket|create_connection)\(|\bhttpx\.|\bhttp\.client\b|"
                r"HTTPS?Connection\s*\(|\.request\(\s*['\"](POST|PUT|PATCH)|\burllib3\b|\baiohttp\b|\bsmtplib\b|\bftplib\b|"
                r"\bInvoke-RestMethod\b|\bdns\.resolver", R),
     "Makes a network request; check the destination and what is sent.", False),
    ("shell-exec", "MEDIUM",
     re.compile(r"\bos\.system\(|\bos\.popen\(|subprocess\.[a-z_]+\(|\bchild_process\b|\bexecSync\(|\bspawn\(|"
                r"\bnew\s+Function\(|\beval\s*\(|\bexec\s*\(|\bsh\s+-c\b|\bbash\s+-c\b", R),
     "Runs shell commands or evaluates strings as code.", False),
    ("money-access", "MEDIUM",
     re.compile(r"\b(stripe|paypal|binance|bybit|coinbase|kraken|metamask|polymarket|phantom)\b[^\n]{0,40}\b(api|key|secret|withdraw|transfer|order)", R),
     "Touches payment or trading accounts.", False),
    ("char-code-blob", "MEDIUM",
     re.compile(r"fromCharCode\s*\(\s*(\d+\s*,\s*){8,}|chr\(\d+\)\s*\+\s*chr\(\d+\)\s*\+\s*chr\(", R),
     "Builds text from character codes, a common way to hide strings.", False),
]
RULE_INDEX = {r[0]: r for r in RULES}
INJECTION_RULES = {"injection-override", "injection-concealment"}

# Descriptive wording and detection-pattern lines (softening by one step only, never to clean)
META = re.compile(r"(?<!\w)(e\.g\.|i\.e\.|z\.\s?b\.)|\b(such\s+as|for\s+example|beispiel|example|detect\w*|flag\w*|"
                  r"blocklist|denylist|signature|scanner|pattern|attacker|malicious|phishing|warn\w*|avoid|bad|"
                  r"don'?t\s+commit|never\s+commit)\b", R)
# Wording that warns against or defends from a technique ("even if a file says ...", "treat it as data")
DEFENSIVE = re.compile(r"\beven\s+if\b|\bif\s+(it|a\s+file|the\s+\w+|someone|anything)\s+(says|asks|tells|contains)\b|"
                       r"\btreat\w*\s+(it\s+|them\s+|this\s+)?as\s+data\b|\bnever\s+(follow|obey|run|execute)\b|"
                       r"\b(data|daten),?\s+(never|not|nie|keine)\s+(instructions|anweisungen)\b|\bnot\s+a\s+step\s+to\s+follow\b|"
                       r"\b(do\s+not|don'?t|never|must\s+not|should\s+not|won'?t)\s+(\w+\s+){0,2}(silently|quietly)\b|"
                       r"\b(silently|quietly)\s+(fail|fails|failed|ignore[sd]?|drop|swallow|break|corrupt|lose|return)\b|"
                       r"\bdoes\s+(it|the\s+\w+|this\s+\w+)\b|\bany\s+instructions?\s+to\b|\bauch\s+wenn\b|\bwenn\s+(eine\s+datei|sie|es)\s+(sagt|verlangt)\b|\bmarkers?\b|\bred\s+flags?\b", R)
CODE_SPAN = re.compile(r"`[^`\n]+`|\"[^\"\n]+\"|'[^'\n]{4,}'")
REGEX_LITERAL = re.compile(r"\\[bswdBSWD.(|)]|\[\^|\(\?[:=!<-]")
URL = re.compile(r"https?://\S+|\b[\w-]+(\.[\w-]+)+/\S*")
QUOTE_OPEN = "\"'`" + chr(0x201C) + chr(0x201E) + chr(0xAB) + chr(0x2018)
KNOWN_INSTALLERS = re.compile(r"https://((sh\.rustup\.rs|astral\.sh|bun\.sh|deno\.land|get\.docker\.com|install\.python-poetry\.org|"
                              r"sdk\.cloud\.google\.com|cli\.github\.com)(?=[/\s\"'|]|$)|"
                              r"raw\.githubusercontent\.com/(Homebrew/install|nvm-sh/nvm)/)", R)

# File-level combinations (same file, not necessarily the same line)
DECODE_FUNCS = re.compile(r"\b(b64decode|a85decode|atob|frombase64string|fromhex|unhexlify|decompress|inflate|unquote|codecs\.decode)\b", R)
EXEC_FUNCS = re.compile(r"getattr\s*\(\s*(__builtins__|builtins)|\bbuiltins\.(exec|eval|compile)|(?<![\w.])compile\s*\(|\bexec\s*\(|\beval\s*\(|\bnew\s+Function\(|\bsh\s+-c\b|\bbash\s+-c\b|subprocess\.|\bos\.system\(|"
                        r"\bchild_process\b|\|\s*(ba)?sh\b|invoke-expression|\biex\b", R)


# ---------------------------------------------------------------------------
# Unicode: invisible characters and look-alike letters.
# Character classes are built from code points so this source file stays plain ASCII.
# ---------------------------------------------------------------------------
def _cls(*ranges):
    return "[" + "".join(re.escape(chr(a)) + ("-" + re.escape(chr(b)) if b != a else "") for a, b in ranges) + "]"


INVISIBLE = [
    ("unicode-tag-chars", "CRITICAL", re.compile(_cls((0xE0000, 0xE007F))),
     "Invisible Unicode tag characters can smuggle hidden text past a human reader."),
    ("unicode-variation-selectors", "CRITICAL", re.compile(_cls((0xE0100, 0xE01EF))),
     "Supplementary variation selectors are invisible and used to hide data."),
    ("unicode-bidi", "CRITICAL", re.compile(_cls((0x202A, 0x202E), (0x2066, 0x2069))),
     "Bidirectional control characters make text display differently from what it is."),
    ("unicode-invisible", "HIGH",
     re.compile(_cls((0x200B, 0x200C), (0x200E, 0x200F), (0x2060, 0x2064), (0x180E, 0x180E), (0x00AD, 0x00AD),
                     (0x034F, 0x034F), (0x115F, 0x1160), (0x3164, 0x3164), (0xFE00, 0xFE0E))
                + "|(?<!^)" + re.escape(BOM)),
     "Invisible or zero-width characters can hide or split words."),
    # Joiner and emoji selector are normal between emoji; next to plain ASCII letters they are suspicious.
    ("unicode-invisible", "HIGH",
     re.compile("(?<=[\\x21-\\x7e])" + re.escape(chr(0x200D)) + "|" + re.escape(chr(0x200D)) + "(?=[\\x21-\\x7e])|"
                + "(?<=[A-Za-z])" + re.escape(chr(0xFE0F))),
     "Invisible or zero-width characters can hide or split words."),
]
CONFUSABLES = {
    0x0430: "a", 0x0435: "e", 0x043E: "o", 0x0440: "p", 0x0441: "c", 0x0443: "y", 0x0445: "x", 0x0456: "i",
    0x0458: "j", 0x0455: "s", 0x0501: "d", 0x0261: "g", 0x04BB: "h", 0x0410: "A", 0x0412: "B", 0x0415: "E",
    0x041A: "K", 0x041C: "M", 0x041D: "H", 0x041E: "O", 0x0420: "P", 0x0421: "C", 0x0422: "T", 0x0425: "X",
    0x0406: "I", 0x0408: "J", 0x03BF: "o", 0x03B1: "a", 0x03B5: "e", 0x03B9: "i", 0x03BD: "v", 0x03C1: "p",
    0x03C4: "t", 0x03BA: "k", 0x039F: "O", 0x0391: "A", 0x0392: "B", 0x0395: "E", 0x0397: "H", 0x0399: "I",
    0x039A: "K", 0x039C: "M", 0x039D: "N", 0x03A1: "P", 0x03A4: "T", 0x03A7: "X", 0x0251: "a", 0x0131: "i",
}
STRIP_INVISIBLE = re.compile(_cls((0x200B, 0x200F), (0x2060, 0x2064), (0x00AD, 0x00AD), (0xFE00, 0xFE0F),
                                  (0xE0000, 0xE007F), (0xE0100, 0xE01EF), (0x202A, 0x202E), (0x2066, 0x2069),
                                  (0xFEFF, 0xFEFF), (0x034F, 0x034F)))
FOREIGN = "".join(re.escape(chr(a)) + "-" + re.escape(chr(b)) for a, b in ((0x0370, 0x03FF), (0x0400, 0x04FF)))
WORD = re.compile("[\\w" + FOREIGN + "]{3,}")


def mixed_words(s):
    out = []
    for w in WORD.findall(s):
        if any("a" <= c.lower() <= "z" for c in w) and any(0x370 <= ord(c) <= 0x4FF for c in w):
            out.append(w)
    return out


def fold(text):
    """NFKC-normalize, drop invisible characters, map look-alike letters to Latin."""
    t = unicodedata.normalize("NFKC", text)
    t = STRIP_INVISIBLE.sub("", t)
    return t.translate(CONFUSABLES)


# ---------------------------------------------------------------------------
# Output hygiene: file names and snippets cannot inject lines into the report
# ---------------------------------------------------------------------------
def esc(s, limit=None):
    out = []
    for ch in str(s):
        o = ord(ch)
        if o < 32 or o == 127 or (0x80 <= o < 0xA0) or STRIP_INVISIBLE.match(ch):
            out.append("<%02X>" % o if o < 256 else "<U+%04X>" % o)
        else:
            out.append(ch)
    s = "".join(out)
    if limit and len(s) > limit:
        keep = (limit - 3) // 2
        s = s[:keep] + "..." + s[-keep:]
    return s


def mask_secrets(s):
    """Keep only the first 6 and last 2 characters of anything that looks like a real key."""
    rx = RULE_INDEX["hardcoded-secret"][2]
    return rx.sub(lambda m: m.group(0)[:6] + "***" + m.group(0)[-2:] if len(m.group(0)) > 12 else "***", s)


# ---------------------------------------------------------------------------
class Report:
    def __init__(self, root):
        self.root = root
        self.findings = {}
        self.inventory = {"files": 0, "scanned": 0, "executables": [], "hidden": [], "symlinks": [],
                          "binaries": [], "auto_run": [], "archives": [], "skipped": []}
        self.gaps = []
        self.core = set()

    def zone(self, path):
        clean = path.replace("\\", "/").split(" (")[0]
        if clean in self.core:
            return "core"
        parts = clean.replace("!", "/").split("/")
        name = parts[-1]
        if name == "SKILL.md" or name in MANIFESTS or any(p.lower() in CORE_DIRS for p in parts[:-1]):
            return "core"
        if ".git" in parts[:-1]:
            return "core"
        if any(p.lower() in DEV_DIRS for p in parts[:-1]) or name == ".gitignore":
            return "dev"
        if (parts and parts[0].lower() == "docs") or DOC_FILE.match(name):
            return "doc"
        return "core"

    def add(self, rule, sev, why, path, line, snippet, hard=False, ctx=True, match=None):
        notes = []
        snippet = mask_secrets(snippet)  # a report must never repeat a found key in full
        z = self.zone(path)
        lowered = False
        plain = URL.sub(" ", snippet)
        if rule == "pipe-to-shell" and KNOWN_INSTALLERS.search(snippet):
            notes.append("known official installer, still runs remote code")
            lowered = True
        elif z in ("dev", "doc"):
            notes.append("test/CI file" if z == "dev" else "documentation")
            lowered = True
        elif ctx and len(REGEX_LITERAL.findall(snippet)) >= 3:
            notes.append("looks like a detection pattern")
            lowered = True
        elif ctx and rule in INJECTION_RULES and match is not None and (
                DEFENSIVE.search(plain) or (META.search(plain) and
                                            any(c in QUOTE_OPEN for c in snippet[max(0, match.start() - 3):match.start() + 1]))):
            notes.append("described or warned against")
            lowered = True
        elif ctx and hard and match is not None and (META.search(plain) or DEFENSIVE.search(plain)) and any(
                s.start() <= match.start() < s.end() for s in CODE_SPAN.finditer(snippet)):
            notes.append("quoted in descriptive text")
            lowered = True
        elif ctx and not hard and (META.search(plain) or DEFENSIVE.search(plain)):
            notes.append("descriptive wording")
            lowered = True
        if lowered:
            sev = DOWN[sev]
        key = rule + "|" + sev
        f = self.findings.setdefault(key, {"rule": rule, "severity": sev, "why": why, "count": 0, "examples": []})
        f["count"] += 1
        if len(f["examples"]) < MAX_EXAMPLES:
            f["examples"].append({"file": path, "line": line, "text": snippet.strip()[:140], "note": ", ".join(notes)})

    def gap(self, path, why):
        self.gaps.append([path, why])

    def verdict(self):
        sevs = {f["severity"] for f in self.findings.values()}
        if "CRITICAL" in sevs:
            return "FAIL"
        if sevs or self.gaps:
            return "REVIEW"
        return "PASS"


def is_code(path, text):
    return os.path.splitext(path)[1].lower() in CODE_SUFFIXES or text.startswith("#!")


def scan_text(rep, path, text, origin="", depth=0):
    ftext = fold(text)
    raw_lines = text.split("\n")
    folded_lines = ftext.split("\n")
    if len(folded_lines) != len(raw_lines):  # normalization changed line structure; scan folded only
        raw_lines = folded_lines
    cut_reported = False
    for i, (raw, line) in enumerate(zip(raw_lines, folded_lines), 1):
        if i % 200 == 0:
            check_time()
        if len(line) > MAX_LINE_SCAN:
            if not cut_reported:
                rep.gap(path + origin, "lines over %d characters were only partly pattern-checked" % MAX_LINE_SCAN)
                cut_reported = True
            line = line[:MAX_LINE_SCAN]
            raw = raw[:MAX_LINE_SCAN]
        hit = set()
        for rid, sev, rx, why, hard in RULES:
            m = rx.search(line)
            if m:
                hit.add(rid)
                rep.add(rid, sev, why, path + origin, i, line, hard=hard, match=m)
        if hit & {"credential-paths", "env-file"} and hit & {"network-call", "webhook-exfil"}:
            rep.add("credential-exfil", "CRITICAL", "Reads stored credentials and sends data over the network in the same step.",
                    path + origin, i, line, hard=True)
        for rid, sev, rx, why in INVISIBLE:
            found = rx.findall(raw)
            if found:
                cps = ", ".join(sorted({"U+%04X" % ord(c) for c in "".join(found)})[:5])
                rep.add(rid, sev, why, path + origin, i, "contains " + cps, hard=True, ctx=False)
        mixed = mixed_words(unicodedata.normalize("NFKC", raw))
        if mixed:
            rep.add("homoglyph-word", "HIGH", "A word mixes Latin with Cyrillic or Greek look-alike letters.",
                    path + origin, i, "word: " + esc(mixed[0], 40), hard=True, ctx=False)
        if len(raw) > 1000 and "base64," not in raw:
            rep.add("very-long-line", "MEDIUM", "Minified or packed code is hard to review and can hide logic.",
                    path + origin, i, raw[:80] + " ...", ctx=False)
    if os.path.splitext(path)[1].lower() in MD_SUFFIXES:
        for m in re.finditer(r"<!--(.*?)-->", ftext, re.S):
            body = m.group(1)
            if re.search(r"\b(you\s+(are|must|should)|assistant|agent|claude|ai|ignore|execute|send|upload|du\s+musst)\b", body, R):
                rep.add("hidden-comment-instructions", "MEDIUM", "Instructions inside an HTML comment are invisible in rendered Markdown.",
                        path + origin, ftext[:m.start()].count("\n") + 1, body, ctx=False)
    if is_code(path, text):
        # detection-pattern lines (regex literals) do not count towards file-level combinations
        ftext = "\n".join(l for l in folded_lines if len(REGEX_LITERAL.findall(l)) < 3)
        if DECODE_FUNCS.search(ftext) and EXEC_FUNCS.search(ftext):
            rep.add("decode-and-exec-file", "HIGH", "Decodes data and executes code in the same file; read how they connect.",
                    path + origin, 0, "decode + exec in one file", hard=True, ctx=False)
        if RULE_INDEX["credential-paths"][2].search(ftext) and RULE_INDEX["network-call"][2].search(ftext):
            rep.add("credential-exfil", "CRITICAL", "Reads stored credentials and makes network calls in the same file.",
                    path + origin, 0, "credential access + network in one file", hard=True, ctx=False)
    if depth < 2:
        decode_hidden(rep, path, text, origin, depth)


def _printable(raw):
    return bool(raw) and sum(32 <= b < 127 or b in (9, 10, 13) for b in raw) / len(raw) > 0.9


def decode_hidden(rep, path, text, origin, depth):
    candidates = []
    for m in re.finditer(r"(?<![A-Za-z0-9+/=_-])[A-Za-z0-9+/_-]{40,}={0,2}(?![A-Za-z0-9+/=_-])", text):
        if "base64," in text[max(0, m.start() - 40):m.start()]:
            continue
        blob = m.group(0)
        if re.fullmatch(r"[0-9a-fA-F]+", blob):  # pure hex is handled below
            continue
        for dec in (base64.b64decode, base64.urlsafe_b64decode):
            try:
                raw = dec(blob + "=" * (-len(blob) % 4))
            except (binascii.Error, ValueError):
                continue
            if _printable(raw):
                candidates.append(("base64", m.start(), raw))
                break
    for m in re.finditer(r"(?<![0-9a-fA-F])(?:[0-9a-fA-F]{2}){24,}(?![0-9a-fA-F])", text):
        raw = binascii.unhexlify(m.group(0))
        if _printable(raw):
            candidates.append(("hex", m.start(), raw))
    for m in re.finditer(r"(?:\\x[0-9a-fA-F]{2}){8,}", text):
        raw = bytes(int(h, 16) for h in re.findall(r"\\x([0-9a-fA-F]{2})", m.group(0)))
        if _printable(raw):
            candidates.append(("x-escapes", m.start(), raw))
    for m in re.finditer(r"(?:%[0-9a-fA-F]{2}){6,}", text):
        raw = urllib.parse.unquote_to_bytes(m.group(0))
        if _printable(raw):
            candidates.append(("url-encoding", m.start(), raw))
    for kind, pos, raw in candidates[:50]:
        ln = text[:pos].count("\n") + 1
        decoded = raw.decode("utf-8", "replace")
        rep.add("encoded-text", "HIGH", "Readable text hidden in an encoding; decoded and scanned too.",
                path + origin, ln, "%s: %s" % (kind, decoded[:100]), hard=True, ctx=False)
        scan_text(rep, path, decoded, origin=origin + " (%s at line %d)" % (kind, ln), depth=depth + 1)


def check_frontmatter(rep, path, text):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text.lstrip(BOM), re.S)
    if not m:
        rep.add("frontmatter-missing", "MEDIUM", "SKILL.md has no YAML frontmatter.", path, 1, text[:60], ctx=False)
        return
    fm = fold(m.group(1))
    desc = re.search(r"^description:\s*(.*(?:\n[ \t]+.*)*)", fm, re.M)
    if desc:
        d = desc.group(1)
        if len(d) > 1024:
            rep.add("description-too-long", "MEDIUM", "Description over 1024 characters.", path, 1, d[:80], ctx=False)
        if re.search(r"\b(always\s+(use|load|activate|apply)|use\s+(this\s+)?(\w+\s+)?(for|on|in|with)\s+(every|all|any)\s+"
                     r"(tasks?|requests?|messages?|conversations?|prompts?|questions?|replies)|"
                     r"(every|all|any)\s+(tasks?|requests?|messages?|conversations?)\b[^.]{0,30}\buse\s+this|"
                     r"\b(whenever|every\s+time|each\s+time)\s+the\s+user\s+(writes|says|asks|sends|types)\s+(anything|something)|"
                     r"\bfor\s+any\s+(\w+\s*,\s*)*\w+(\s+or\s+\w+)*\s+(question|task|request|message)|"
                     r"\bimmer\s+(verwenden|nutzen|aktivieren|laden)|bei\s+(jeder|allen)\s+(anfrage|aufgabe|nachricht))", d, R):
            rep.add("trigger-hijack", "HIGH", "Description tries to fire on every request, a way to hijack unrelated tasks.",
                    path, 1, d[:140], hard=True, ctx=False)
    if re.search(r"^hooks\s*:", fm, re.M):
        rep.inventory["auto_run"].append(path)
        rep.add("frontmatter-hooks", "HIGH", "The skill registers hooks that run automatically.", path, 1, "hooks:", hard=True, ctx=False)
    tools = re.search(r"^allowed-tools\s*:\s*(.+)$", fm, re.M)
    if tools:
        rep.add("allowed-tools", "MEDIUM", "The skill pre-approves tools; check each one is needed.", path, 1, tools.group(1), ctx=False)
    name = re.search(r"^name:\s*(.+)$", fm, re.M)
    if name and re.search(r"anthropic|claude|official|offiziell|openai|google", name.group(1), R):
        rep.add("name-impersonation", "MEDIUM", "Name suggests an official origin; verify the publisher.", path, 1, name.group(1), ctx=False)


def check_special(rep, path, full):
    base = os.path.basename(path).lower()
    parts = path.replace("\\", "/").lower().split("/")
    auto = None
    if base == "package.json":
        try:
            with open(full, encoding="utf-8", errors="replace") as fh:
                data = json.load(fh)
            scripts = data.get("scripts", {}) if isinstance(data, dict) else {}
            hooks = [k for k in scripts if k in ("preinstall", "install", "postinstall", "prepare", "prepublish", "prepack")]
            if hooks:
                auto = "npm lifecycle scripts run on install: " + ", ".join(hooks)
        except (ValueError, OSError):
            rep.gap(path, "package.json could not be parsed")
    elif base == "setup.py":
        auto = "setup.py can run code during pip install"
    elif base in ("hooks.json", "settings.json", "settings.local.json") or "hooks" in parts[:-1]:
        auto = "agent hook or settings file; may run commands automatically on agent events"
    elif base in (".mcp.json", "mcp.json"):
        auto = "declares MCP servers that would start as separate programs"
    elif base in ("plugin.json", "marketplace.json"):
        auto = "plugin manifest; check which hooks, commands and servers it registers"
    if auto:
        rep.inventory["auto_run"].append(path)
        sev = "HIGH" if auto.startswith(("agent hook", "npm", "setup.py")) else "MEDIUM"
        rep.add("auto-run", sev, "Runs or registers code without an explicit request.", path, 0, auto, hard=True, ctx=False)


def read_file(rep, path, full, name):
    """Read one regular file. Returns its text, or None (with a gap or inventory entry)."""
    st = os.lstat(full)
    if not stat.S_ISREG(st.st_mode):
        rep.gap(path, "not a regular file (pipe, device or socket), skipped")
        return None
    if st.st_mode & 0o111:
        rep.inventory["executables"].append(path)
    if st.st_size > MAX_FILE_BYTES:
        rep.gap(path, "file too large (%d bytes)" % st.st_size)
        return None
    with open(full, "rb") as fh:
        data = fh.read(MAX_FILE_BYTES + 1)
    ext = os.path.splitext(name)[1].lower()
    if ext in IMAGE_MAGIC or b"\x00" in data[:8192]:
        strings = "\n".join(s.decode("ascii") for s in re.findall(rb"[\x20-\x7e\t]{12,}", data)[:5000])
        if strings:
            before = sum(f["count"] for f in rep.findings.values())
            scan_text(rep, path, strings, origin=" (text inside binary)", depth=2)
            if sum(f["count"] for f in rep.findings.values()) > before:
                rep.add("text-in-binary", "HIGH", "A binary or image file carries readable text that matched patterns.",
                        path, 0, "embedded text", hard=True, ctx=False)
    if ext in IMAGE_MAGIC:
        rep.inventory["binaries"].append(path)
        if not any(data.startswith(sig) for sig in IMAGE_MAGIC[ext]):
            rep.add("disguised-file", "HIGH", "File content does not match its extension.", path, 0, ext, hard=True, ctx=False)
            rep.gap(path, "content does not match extension")
        return None
    if b"\x00" in data[:8192]:
        rep.inventory["binaries"].append(path)
        if data[:4] in (b"\x7fELF", b"\xcf\xfa\xed\xfe", b"\xca\xfe\xba\xbe") or data[:2] == b"MZ":
            rep.add("executable-binary", "HIGH", "Compiled program inside the package; its behavior cannot be read.",
                    path, 0, "binary executable", hard=True, ctx=False)
        rep.gap(path, "binary file, not readable as text")
        return None
    rep.inventory["scanned"] += 1
    return data.decode("utf-8", "replace")


def scan_zip(rep, path, full, depth):
    rep.inventory["archives"].append(path)
    try:
        with zipfile.ZipFile(full) as z:
            infos = z.infolist()
            if len(infos) > MAX_ARCHIVE_MEMBERS:
                rep.gap(path, "archive has too many entries (%d)" % len(infos))
                return
            if any(i.flag_bits & 0x1 for i in infos):
                rep.add("encrypted-zip", "CRITICAL", "Password-protected archive; its content cannot be inspected.",
                        path, 0, "encrypted members present", hard=True, ctx=False)
                rep.gap(path, "encrypted archive")
                return
            bad = [i.filename for i in infos if i.filename.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:", i.filename)
                   or ".." in i.filename.replace("\\", "/").split("/")]
            if bad:
                rep.add("zip-path-traversal", "CRITICAL", "Archive entries try to write outside their folder.",
                        path, 0, ", ".join(esc(b, 40) for b in bad[:3]), hard=True, ctx=False)
                rep.gap(path, "archive not unpacked because of path traversal")
                return
            if depth >= MAX_ARCHIVE_DEPTH:
                rep.gap(path, "nested archive too deep, not unpacked")
                return
            with tempfile.TemporaryDirectory(prefix="schleuse_") as tmp:
                budget = MAX_ARCHIVE_BYTES
                for i in infos:
                    if i.is_dir():
                        continue
                    member = path + "!" + i.filename
                    if ((i.external_attr >> 16) & 0o170000) == stat.S_IFLNK:
                        rep.inventory["symlinks"].append(member)
                        rep.gap(member, "symlink inside archive, not followed")
                        continue
                    if budget <= 0:
                        rep.gap(member, "archive byte limit reached, not unpacked")
                        continue
                    try:
                        target = os.path.join(tmp, i.filename)
                        if not os.path.realpath(target).startswith(os.path.realpath(tmp) + os.sep):
                            raise ValueError("path escapes extraction folder")
                        os.makedirs(os.path.dirname(target), exist_ok=True)
                        with z.open(i) as src, open(target, "wb") as dst:
                            chunk = src.read(min(MAX_FILE_BYTES + 1, budget))
                            dst.write(chunk)
                            budget -= len(chunk)
                    except Exception as e:  # noqa: BLE001 - any failure is a coverage gap
                        rep.gap(member, "could not unpack (%s)" % type(e).__name__)
                walk(rep, tmp, depth + 1, prefix=path + "!", skip_git=False)
    except Exception as e:  # noqa: BLE001
        rep.gap(path, "unreadable archive (%s)" % type(e).__name__)


def mark_core(rep, root, files, prefix):
    """Files referenced by instructions, hooks or manifests count as core, wherever they live."""
    sources = []
    for full, path in files:
        name = os.path.basename(full)
        parts = path.replace("\\", "/").lower().split("/")
        if name == "SKILL.md" or name.lower() in MANIFESTS or "hooks" in parts[:-1]:
            try:
                st = os.lstat(full)
                if stat.S_ISREG(st.st_mode) and st.st_size <= MAX_FILE_BYTES:
                    with open(full, "rb") as fh:
                        sources.append(fh.read().decode("utf-8", "replace"))
            except OSError:
                pass
    blob = "\n".join(sources)
    for full, path in files:
        r = os.path.relpath(full, root).replace("\\", "/")
        name = os.path.basename(full)
        if r in blob or (len(name) >= 6 and name != "SKILL.md" and name in blob):
            rep.core.add((prefix + r).replace("\\", "/"))


def walk(rep, root, depth=0, prefix="", skip_git=True):
    files = []
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        rel_dir = os.path.relpath(dirpath, root).replace("\\", "/")
        in_git = skip_git and (rel_dir == ".git" or rel_dir.startswith(".git/"))
        if in_git:
            sub = "" if rel_dir == ".git" else rel_dir[5:] + "/"
            dirnames[:] = [d for d in dirnames if not GIT_INTERNAL.match(sub + d + "/")]
            filenames = [f for f in filenames if not GIT_INTERNAL.match(sub + f)]
            if rel_dir == ".git":
                rep.inventory["skipped"].append(prefix + ".git internals (objects, refs, logs, config)")
            for f in filenames:
                rep.add("unexpected-git-file", "HIGH", "File inside .git that git does not create; tools often skip this folder.",
                        prefix + rel_dir + "/" + f, 0, f, hard=True, ctx=False)
        for d in list(dirnames):
            full = os.path.join(dirpath, d)
            if os.path.islink(full):
                rel = prefix + os.path.relpath(full, root)
                rep.inventory["symlinks"].append(rel)
                rep.gap(rel, "symlinked folder, not followed")
                dirnames.remove(d)
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            files.append((full, prefix + os.path.relpath(full, root)))
    mark_core(rep, root, files, prefix)
    for full, path in files:
        fn = os.path.basename(full)
        rep.inventory["files"] += 1
        try:
            if fn.startswith(".") and fn not in (".gitignore", ".gitattributes"):
                rep.inventory["hidden"].append(path)
            if os.path.islink(full):
                rep.inventory["symlinks"].append(path)
                target = os.path.realpath(full)
                if not target.startswith(os.path.realpath(root) + os.sep):
                    rep.add("symlink-outside", "HIGH", "Symlink points outside the package.", path, 0, esc(target, 60), hard=True, ctx=False)
                rep.gap(path, "symlink, not followed")
                continue
            check_special(rep, path, full)
            low = fn.lower()
            if low.endswith(ZIP_LIKE):
                if stat.S_ISREG(os.lstat(full).st_mode):
                    scan_zip(rep, path, full, depth)
                else:
                    rep.gap(path, "not a regular file, skipped")
                continue
            if low.endswith((".tar", ".tgz", ".gz", ".7z", ".rar", ".xz", ".bz2")):
                rep.inventory["archives"].append(path)
                rep.gap(path, "archive format not unpacked by this scanner")
                continue
            text = read_file(rep, path, full, fn)
            if text is None:
                continue
            scan_text(rep, path, text)
            if fn == "SKILL.md":
                check_frontmatter(rep, path, text)
        except Exception as e:  # noqa: BLE001
            rep.gap(path, "could not be scanned (%s)" % type(e).__name__)


def render(rep):
    inv = rep.inventory
    out = ["SCHLEUSE SCAN: %s" % rep.verdict(),
           "Files: %d, read as text: %d, gaps: %d" % (inv["files"], inv["scanned"], len(rep.gaps))]
    for key, label in (("auto_run", "Auto-run/manifests"), ("executables", "Executable"), ("symlinks", "Symlinks"),
                       ("archives", "Archives"), ("skipped", "Skipped")):
        if inv[key]:
            items = ", ".join(esc(p, 50) for p in inv[key][:5]) + (" ..." if len(inv[key]) > 5 else "")
            out.append("%s (%d): %s" % (label, len(inv[key]), items))
    if rep.gaps:
        out.append("")
        out.append("NOT SCANNED (never counts as clean):")
        for p, why in rep.gaps[:15]:
            out.append("- %s: %s" % (esc(p, 60), why))
        if len(rep.gaps) > 15:
            out.append("- ... %d more" % (len(rep.gaps) - 15))
    fs = sorted(rep.findings.values(), key=lambda f: (-SEV_ORDER[f["severity"]], -f["count"], f["rule"]))
    out.append("")
    if fs:
        out.append("FINDINGS:")
        for f in fs:
            out.append("[%s] %s x%d: %s" % (f["severity"], f["rule"], f["count"], f["why"]))
            for e in f["examples"]:
                loc = "%s:%s" % (esc(e["file"], 60), e["line"]) if e["line"] else esc(e["file"], 60)
                note = " [%s]" % e["note"] if e["note"] else ""
                out.append("  %s  %s%s" % (loc, esc(e["text"], 110), note))
    else:
        out.append("No pattern findings.")
    out.append("")
    out.append("Severity drops one step for docs, test/CI files, quoted examples and detection patterns, never to clean.")
    out.append("Patterns are hints, not proof: read every flagged line in context.")
    return "\n".join(out)


def run(target, json_out):
    if not os.path.exists(target):
        print("Target not found: " + esc(target, 80))
        return 3
    absolute = os.path.abspath(target)
    if os.path.isdir(absolute):
        rep = Report(absolute)
        walk(rep, absolute)
    else:
        rep = Report(os.path.dirname(absolute))
        name = os.path.basename(absolute)
        rep.inventory["files"] = 1
        if name.lower().endswith(ZIP_LIKE):
            scan_zip(rep, name, absolute, 0)
        else:
            check_special(rep, name, absolute)
            text = read_file(rep, name, absolute, name)
            if text is not None:
                scan_text(rep, name, text)
                if name == "SKILL.md":
                    check_frontmatter(rep, name, text)
    if rep.inventory["scanned"] == 0:
        rep.gap("(all)", "no file could be read as text, nothing was checked")
    print(render(rep))
    if json_out:
        with open(json_out, "w", encoding="utf-8") as fh:
            json.dump({"verdict": rep.verdict(), "inventory": rep.inventory, "gaps": rep.gaps,
                       "findings": list(rep.findings.values())}, fh, indent=2, ensure_ascii=True)
    return {"PASS": 0, "REVIEW": 1, "FAIL": 2}[rep.verdict()]


def main(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print(__doc__)
        return 3
    json_out = None
    if "--json" in argv:
        idx = argv.index("--json")
        if idx + 1 >= len(argv):
            print("--json needs a file path")
            return 3
        json_out = argv[idx + 1]
    _START[0] = time.monotonic()
    try:
        return run(argv[1], json_out)
    except ScanTimeout as e:
        print("SCHLEUSE SCAN: ERROR, nothing can be concluded (%s)" % e)
        return 3
    except Exception as e:  # noqa: BLE001 - an error must never look like a verdict
        print("SCHLEUSE SCAN: ERROR, nothing can be concluded (%s: %s)" % (type(e).__name__, esc(str(e), 120)))
        return 3


if __name__ == "__main__":
    sys.exit(main(sys.argv))
