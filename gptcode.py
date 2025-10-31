#!/usr/bin/env python3
"""
GPTCode – Chat-first DevOps/Coding Assistent (Claude-Style) fürs Terminal
- Start: `gptcode` im Projektordner
- First-Run: fragt API-Key + Modell und legt Config an
- Tools: list_dir, read_file, write_file, apply_patch, run, tail_file, systemctl, docker, pytest
- Modi: :dryrun on/off, :auto on/off, Headless (--headless --goal "..."), CLI-Overrides (--model, --dryrun)
"""
import argparse
import os, sys, json, subprocess, shutil
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple

CONFIG_DIR = Path(os.path.expanduser("~/.config/gptcode"))
CONFIG_FILE = CONFIG_DIR / "config.json"
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_TIMEOUT = int(os.getenv("GPTCODE_TIMEOUT", "60"))  # sec


def check_runtime_prerequisites() -> None:
    """Stellt sicher, dass Kernwerkzeuge im PATH liegen."""

    def _present(binary: str) -> bool:
        return shutil.which(binary) is not None

    missing_required = []
    optional_warnings = []

    requirements = (
        ("git", True, "Installiere git (z. B. `sudo apt install git`) oder siehe https://git-scm.com/downloads."),
        (
            "docker",
            True,
            "Installiere Docker Engine inkl. Compose Plugin (siehe https://docs.docker.com/engine/install/).",
        ),
        (
            "pytest",
            False,
            "Optionaler Test-Runner. Installiere via `pip install pytest` oder siehe https://docs.pytest.org/en/stable/.",
        ),
    )

    for binary, required, hint in requirements:
        if _present(binary):
            continue
        message = f"- {binary}: {hint}"
        if required:
            missing_required.append(message)
        else:
            optional_warnings.append(message)

    if optional_warnings:
        print(
            "[HINWEIS] Empfohlene Zusatztools fehlen:\n" + "\n".join(optional_warnings),
            file=sys.stderr,
        )

    if missing_required:
        print(
            "[FEHLER] Erforderliche Werkzeuge fehlen. Bitte installieren und erneut starten:\n"
            + "\n".join(missing_required),
            file=sys.stderr,
        )
        sys.exit(1)

def ensure_config():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if CONFIG_FILE.exists():
        return
    print("\n✨ GPTCode Ersteinrichtung ✨\n")
    api_key = input("Bitte gib deinen OpenAI API-Key ein: ").strip()
    while not api_key:
        api_key = input("API-Key darf nicht leer sein. Bitte erneut: ").strip()
    model = input(f"Bevorzugtes Modell [{DEFAULT_MODEL}]: ").strip() or DEFAULT_MODEL
    cfg = {"api_key": api_key, "model": model, "dryrun": False}
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2))
    print(f"\n✅ Gespeichert in {CONFIG_FILE}\n")

def load_config() -> dict:
    ensure_config()
    return json.loads(CONFIG_FILE.read_text())

def save_config(cfg: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2))

try:
    from openai import OpenAI
except Exception:
    OpenAI = None  # type: ignore[assignment]

SYSTEM_PROMPT_TMPL = (
    "Du bist ein Chat-first DevOps/Coding-Assistent (Claude-Style). "
    "Arbeite vom aktuellen Ordner aus: {cwd}. "
    "Wenn du Aktionen brauchst, gib **nur JSON** mit einem Tool-Call zurück. "
    "Schema: {\\n\"tool\": \"list_dir|read_file|write_file|apply_patch|run|tail_file|systemctl|docker|pytest\", \"args\": {...}\\n}. "
    "Tool-Args: run:{cmd,timeout?,env?}, tail_file:{path,lines?}, systemctl:{action,status|restart|start|stop|daemon-reload,unit}, "
    "docker:{action,service?}, pytest:{path?,k?}. "
    "Bevor du schreibst/ausführst: kurz begründen und nach Bestätigung fragen (oder im Auto-Modus nur ankündigen). "
    "Kleine Schritte. Nach jeder Aktion Ergebnis zusammenfassen und nächsten Schritt vorschlagen."
)

HELP = (
    ":help – Hilfe\n"
    ":cwd – aktuelles Verzeichnis\n"
    ":cd <pfad> – wechseln\n"
    ":yes / :no – letzte Aktion erlauben/ablehnen\n"
    ":dryrun on|off – Schreib/Ausführ-Dry-Run\n"
    ":auto on|off – Schritte automatisch erlauben (vorsichtig!)\n"
    ":quit – beenden\n"
)

@dataclass
class Session:
    client: Any
    model: str
    dryrun: bool = False
    auto: bool = False
    messages: List[Dict[str, str]] = field(default_factory=list)
    pending_action: Optional[Dict[str, Any]] = None
    def add(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})

def run_model(sess: Session) -> str:
    sys_prompt = SYSTEM_PROMPT_TMPL.format(cwd=str(Path.cwd()))
    resp = sess.client.chat.completions.create(
        model=sess.model,
        messages=[{"role":"system","content":sys_prompt}] + sess.messages,
        temperature=0.2,
    )
    return resp.choices[0].message.content

def list_dir(path: str) -> str:
    p = Path(path).expanduser().resolve()
    if not p.exists():
        return f"[list_dir] Pfad existiert nicht: {p}"
    if p.is_file():
        return f"[list_dir] {p} ist eine Datei"
    rows=[]
    for c in sorted(p.iterdir()):
        k = "d" if c.is_dir() else "f"
        rows.append(f"{k}\t{c.name}")
    return f"[list_dir] {p}\n" + "\n".join(rows)

def read_file(path: str) -> str:
    p = Path(path).expanduser().resolve()
    if not p.exists() or not p.is_file():
        return f"[read_file] Datei nicht gefunden: {p}"
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return f"[read_file] Fehler: {e}"

def write_file(path: str, content: str, dry: bool=False) -> str:
    p = Path(path).expanduser().resolve()
    if dry:
        return f"[write_file:DRYRUN] Würde schreiben: {p} (len={len(content)}B)"
    p.parent.mkdir(parents=True, exist_ok=True)
    try:
        old = p.read_text(encoding="utf-8", errors="ignore") if p.exists() else None
        p.write_text(content, encoding="utf-8")
        return f"[write_file] Geschrieben: {p} (alt: {len(old or '')}B, neu: {len(content)}B)"
    except Exception as e:
        return f"[write_file] Fehler: {e}"

def apply_patch(patch_text: str, dry: bool=False) -> str:
    if dry:
        return "[apply_patch:DRYRUN] Würde Patch anwenden (git apply -p0)."
    try:
        proc = subprocess.run(["git","apply","-p0","-"], input=patch_text.encode(),
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if proc.returncode == 0:
            return "[apply_patch] Patch angewendet."
        return f"[apply_patch] Fehler (rc={proc.returncode}):\n{proc.stderr.decode()}"
    except FileNotFoundError:
        return "[apply_patch] git nicht gefunden. Bitte installieren."

def run(cmd: str, timeout: int=DEFAULT_TIMEOUT, env: Optional[dict]=None) -> str:
    try:
        full_env = os.environ.copy()
        if env:
            for k,v in env.items():
                if isinstance(v, str):
                    full_env[k]=v
        proc = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              text=True, timeout=timeout, env=full_env)
        return f"[run] rc={proc.returncode}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
    except subprocess.TimeoutExpired:
        return f"[run] Timeout nach {timeout}s: {cmd}"
    except Exception as e:
        return f"[run] Fehler: {e}"

def tail_file(path: str, lines: int=200) -> str:
    p = Path(path).expanduser().resolve()
    if not p.exists() or not p.is_file():
        return f"[tail_file] Datei nicht gefunden: {p}"
    try:
        with p.open("r", encoding="utf-8", errors="ignore") as f:
            data = f.readlines()[-lines:]
        return "".join(data)
    except Exception as e:
        return f"[tail_file] Fehler: {e}"

def systemctl(action: str, unit: str) -> str:
    if action not in {"status","restart","stop","start","daemon-reload"}:
        return f"[systemctl] Ungültige Action: {action}"
    cmd = ["systemctl", action] + ([unit] if unit and action not in {"daemon-reload"} else [])
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return f"[systemctl] rc={proc.returncode}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
    except Exception as e:
        return f"[systemctl] Fehler: {e}"

def docker_compose(action: str, service: Optional[str]=None) -> str:
    if action not in {"up","down","build","logs"}:
        return f"[docker] Ungültige Action: {action}"
    base = ["docker","compose"]
    if action == "up":
        cmd = base + ["up","-d"] + ([service] if service else [])
    elif action == "down":
        cmd = base + ["down"]
    elif action == "build":
        cmd = base + ["build"] + ([service] if service else [])
    else:
        cmd = base + ["logs","--no-log-prefix","--tail","200"] + ([service] if service else [])
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return f"[docker] rc={proc.returncode}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
    except Exception as e:
        return f"[docker] Fehler: {e}"

def pytest_run(path: str=".", k: Optional[str]=None, timeout: int=DEFAULT_TIMEOUT) -> str:
    cmd = ["pytest","-q",path]
    if k:
        cmd += ["-k", k]
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)
        return f"[pytest] rc={proc.returncode}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
    except FileNotFoundError:
        return "[pytest] nicht gefunden. `pip install pytest` im Projekt/venv."
    except subprocess.TimeoutExpired:
        return f"[pytest] Timeout nach {timeout}s."

def maybe_parse_json(s: str):
    s=s.strip()
    if not (s.startswith('{') and s.endswith('}')):
        return None
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        return None

def dispatch_tool(sess, tool: str, args: dict) -> str:
    if tool == "list_dir":
        return list_dir(args.get("path","."))
    if tool == "read_file":
        return read_file(args.get("path",""))
    if tool == "write_file":
        return write_file(args.get("path",""), args.get("content",""), dry=sess.dryrun)
    if tool == "apply_patch":
        return apply_patch(args.get("patch",""), dry=sess.dryrun)
    if tool == "run":
        t = int(args.get("timeout", DEFAULT_TIMEOUT))
        env = args.get("env") if isinstance(args.get("env"), dict) else None
        if sess.dryrun:
            return f"[run:DRYRUN] Würde ausführen: {args.get('cmd','')} (timeout={t})"
        return run(args.get("cmd",""), timeout=t, env=env)
    if tool == "tail_file":
        return tail_file(args.get("path",""), int(args.get("lines",200)))
    if tool == "systemctl":
        if sess.dryrun:
            return f"[systemctl:DRYRUN] Würde ausführen: systemctl {args.get('action')} {args.get('unit','')}"
        return systemctl(args.get("action","status"), args.get("unit",""))
    if tool == "docker":
        if sess.dryrun:
            return f"[docker:DRYRUN] Würde docker compose {args.get('action')} {args.get('service','')}"
        return docker_compose(args.get("action","logs"), args.get("service"))
    if tool == "pytest":
        if sess.dryrun:
            return "[pytest:DRYRUN] Würde pytest ausführen."
        return pytest_run(args.get("path","."), args.get("k"))
    return f"Unbekanntes Tool: {tool}"

def headless_loop(sess, goal: str, max_steps: int=30):
    sess.add("user", f"Ziel: {goal}. Lege los, arbeite iterativ bis abgeschlossen. Melde Fortschritt kurz.")
    for step in range(1, max_steps+1):
        ai = run_model(sess)
        parsed = maybe_parse_json(ai)
        if parsed and "tool" in parsed:
            result = dispatch_tool(sess, parsed.get("tool",""), parsed.get("args",{}))
            print(result)
            sess.add("user", f"ERGEBNIS ({parsed.get('tool')}):\n{result}")
            continue
        txt = ai.strip().lower()
        print(ai.strip())
        sess.add("assistant", ai)
        if any(k in txt for k in ["fertig","abgeschlossen","done","final"]):
            print("[headless] Fertig gemeldet nach", step, "Schritten.")
            break
    else:
        print("[headless] Max Steps erreicht.")

def determine_session_settings(cfg: Dict[str, Any], model_override: Optional[str]=None,
                               dryrun_override: Optional[bool]=None) -> Tuple[str, bool]:
    model = (model_override or cfg.get("model") or DEFAULT_MODEL)
    dryrun = dryrun_override if dryrun_override is not None else bool(cfg.get("dryrun", False))
    return model, dryrun


def repl(headless: bool=False, goal: Optional[str]=None, auto: Optional[bool]=None,
         model_override: Optional[str]=None, dryrun_override: Optional[bool]=None):
    if OpenAI is None:
        print("[FEHLER] openai-SDK fehlt. Bitte Installer erneut ausführen.", file=sys.stderr)
        sys.exit(1)

    cfg = load_config()
    os.environ["OPENAI_API_KEY"] = cfg.get("api_key","")
    model, dryrun = determine_session_settings(cfg, model_override=model_override,
                                               dryrun_override=dryrun_override)
    client = OpenAI()
    sess = Session(client=client, model=model, dryrun=dryrun)
    if auto is not None:
        sess.auto = auto

    help_text = (
        ":help – Hilfe\n"
        ":cwd – aktuelles Verzeichnis\n"
        ":cd <pfad> – wechseln\n"
        ":yes / :no – letzte Aktion erlauben/ablehnen\n"
        ":dryrun on|off – Schreib/Ausführ-Dry-Run\n"
        ":auto on|off – Schritte automatisch erlauben\n"
        ":quit – beenden\n"
    )
    dry_info = "on" if sess.dryrun else "off"
    print(f"GPTCode bereit – Modell: {sess.model} (dryrun={dry_info})\nProjekt: {Path.cwd()}\n\n{help_text}")

    if headless and goal:
        print("[Headless] Auto-Modus gestartet: ", goal)
        sess.auto = True
        headless_loop(sess, goal)
        return

    while True:
        try:
            user = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print(); break
        if not user:
            continue

        if user == ":quit":
            break
        if user == ":help":
            print(HELP); continue
        if user == ":cwd":
            print(Path.cwd()); continue
        if user.startswith(":cd "):
            target = user[4:].strip()
            try:
                os.chdir(target); print(f"OK: {Path.cwd()}")
            except Exception as e:
                print(f"Fehler: {e}")
            continue
        if user.startswith(":dryrun"):
            _, _, val = user.partition(" ")
            val = val.strip().lower()
            if val in {"on","off"}:
                cfg = load_config()
                cfg["dryrun"] = (val=="on"); save_config(cfg)
                sess.dryrun = (val=="on")
                print(f"dryrun={sess.dryrun}")
            else:
                print(f"dryrun aktuell: {sess.dryrun}")
            continue
        if user.startswith(":auto"):
            _, _, val = user.partition(" ")
            val = val.strip().lower()
            if val in {"on","off"}:
                sess.auto = (val=="on"); print(f"auto={sess.auto}")
            else:
                print(f"auto aktuell: {sess.auto}")
            continue
        if user in (":yes", ":no"):
            if not sess.pending_action:
                print("Keine ausstehende Aktion."); continue
            if user == ":no":
                print("Aktion verworfen."); sess.pending_action=None; continue
            action = sess.pending_action; sess.pending_action=None
            result = dispatch_tool(sess, action.get("tool",""), action.get("args",{}))
            print(result)
            sess.add("user", f"ERGEBNIS ({action.get('tool')}):\n{result}")
            ai = run_model(sess)
            parsed = maybe_parse_json(ai)
            if parsed and "tool" in parsed and "args" in parsed:
                if sess.auto:
                    result = dispatch_tool(sess, parsed.get("tool",""), parsed.get("args",{}))
                    print(result)
                    sess.add("user", f"ERGEBNIS ({parsed.get('tool')}):\n{result}")
                else:
                    sess.pending_action = parsed
                    print("AI möchte ausführen →", json.dumps(parsed, ensure_ascii=False))
                    print("Bestätigen? (:yes / :no)")
            else:
                print(ai.strip()); sess.add("assistant", ai)
            continue

        # Normaler Chat
        sess.add("user", user)
        ai = run_model(sess)
        parsed = maybe_parse_json(ai)
        if parsed and "tool" in parsed and "args" in parsed:
            if sess.auto:
                result = dispatch_tool(sess, parsed.get("tool",""), parsed.get("args",{}))
                print(result)
                sess.add("user", f"ERGEBNIS ({parsed.get('tool')}):\n{result}")
            else:
                sess.pending_action = parsed
                print("AI möchte ausführen →", json.dumps(parsed, ensure_ascii=False))
                print("Bestätigen? (:yes / :no)")
        else:
            print(ai.strip()); sess.add("assistant", ai)

def parse_cli_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="gptcode", description="GPTCode – Chat-first DevOps/Coding Assistent")
    parser.add_argument("--headless", action="store_true", help="Headless-Modus aktivieren")
    parser.add_argument("--goal", metavar="TEXT", help="Zielbeschreibung für Headless-Läufe")
    parser.add_argument("--auto", action="store_true", help="Automatische Freigabe aktivieren")
    parser.add_argument("--model", metavar="NAME", help="Modell nur für diese Sitzung überschreiben")
    parser.add_argument("--dryrun", choices=["on","off"], help="Dry-Run nur für diese Sitzung setzen")
    return parser.parse_args(argv)


if __name__ == "__main__":
    check_runtime_prerequisites()
    cli_args = parse_cli_args(sys.argv[1:])
    ensure_config()
    dry_override = None
    if cli_args.dryrun is not None:
        dry_override = (cli_args.dryrun == "on")
    auto_flag = True if cli_args.auto else None
    repl(
        headless=cli_args.headless,
        goal=cli_args.goal,
        auto=auto_flag,
        model_override=cli_args.model,
        dryrun_override=dry_override,
    )
