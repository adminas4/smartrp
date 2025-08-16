import os
import sys
import yaml
import json
import subprocess
import shlex
import pathlib
from typing import List, Dict, Any

from agent.ai_openai import ask_agent

# --- Preflight: užtikrinam minimalią struktūrą ir priklausomybes ---
def ensure_structure():
    """
    Paruošia minimalų projektą:
    - sukuria backend/, backend/app/, tests/ katalogus ir jų __init__.py, jei trūksta
    - jeigu FastAPI neįdiegtas, įdiegia priklausomybes iš requirements.txt
    """
    for path in ["backend", "backend/app", "tests"]:
        os.makedirs(path, exist_ok=True)
        init_file = os.path.join(path, "__init__.py")
        if not os.path.exists(init_file):
            open(init_file, "w").close()

    try:
        import fastapi  # noqa: F401
    except Exception:
        print("[Preflight] FastAPI nerastas — diegiam priklausomybes iš requirements.txt ...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])


ensure_structure()

HERE = pathlib.Path(__file__).parent
CFG = yaml.safe_load((HERE / "agent_config.yaml").read_text())

ROOT = pathlib.Path(os.getenv("AGENT_ROOT", CFG.get("root_dir", "."))).resolve()
WRITE_WHITELIST = [(ROOT / p).resolve() for p in CFG["write_whitelist"]]
ALLOWED_CMDS = CFG["allowed_commands"]

# --- Apsauga nuo stabilių endpoint'ų perrašymo ---
PROTECTED_PATHS = [
    (ROOT / "backend/app/api/estimate/analyze.py").resolve(),
    (ROOT / "backend/app/api/estimate/update.py").resolve(),
    (ROOT / "backend/app/api/health.py").resolve(),
]

def is_in_whitelist(path: pathlib.Path) -> bool:
    rp = path.resolve()
    return any(str(rp).startswith(str(w)) for w in WRITE_WHITELIST)

def is_protected(path: pathlib.Path) -> bool:
    rp = path.resolve()
    return any(str(rp) == str(p) for p in PROTECTED_PATHS)

def apply_write(path: pathlib.Path, content: str, action: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    if action == "write":
        path.write_text(content, encoding="utf-8")
    elif action == "append":
        with open(path, "a", encoding="utf-8") as f:
            f.write(content)
    elif action == "patch":
        # Minimalus palaikymas: unified diff netaikomas.
        raise RuntimeError(
            "Unified diff ('action: patch') šiuo metu nepalaikomas. "
            "Prašyk agento grąžinti 'action: write' su pilnu failo turiniu."
        )
    else:
        raise ValueError(f"Nežinomas action: {action}")

def run_allowed(cmd: str) -> int:
    cmd = cmd.strip()
    # Leidžiam pagal pirmą žodį (pvz., 'pytest', 'ruff', 'uvicorn', 'npm', 'pip', 'make')
    first_word = cmd.split()[0] if cmd else ""
    allowed_first = {a.split()[0] for a in ALLOWED_CMDS}
    if first_word not in allowed_first:
        raise RuntimeError(f"Komanda neleidžiama: {cmd}")
    print(f"→ Vykdoma: {cmd}")
    proc = subprocess.run(shlex.split(cmd), cwd=str(ROOT))
    return proc.returncode

def repo_map() -> str:
    # Aprašome tik whitelist katalogus (trumpas žemėlapis), ignoruojant neegzistuojančius
    lines = []
    for w in WRITE_WHITELIST:
        try:
            if not w.exists():
                continue
            for p in w.rglob("*"):
                if p.is_file() and p.stat().st_size < 200_000:  # nekeliam milžiniškų failų
                    rel = p.relative_to(ROOT)
                    lines.append(f"- {rel}")
        except Exception:
            # Jei kas nors nepavyksta skaityti (teisės ir pan.) — praleidžiam
            continue
    return "Failų žemėlapis (whitelisted):\n" + "\n".join(lines[:500])

def main():
    if len(sys.argv) < 2:
        print('Naudojimas: python -m agent.runner "Tavo tikslas..."')
        sys.exit(2)

    goal = sys.argv[1]
    context = repo_map()

    plan = ask_agent(goal=goal, context=context)
    print("Agent JSON atsakymas:\n", json.dumps(plan, indent=2, ensure_ascii=False))

    files: List[Dict[str, Any]] = plan.get("files", [])
    for f in files:
        path = ROOT / f["path"]
        action = f.get("action", "write")
        if not is_in_whitelist(path):
            raise RuntimeError(f"Bandoma rašyti už whitelist ribų: {path}")
        if is_protected(path):
            raise RuntimeError(f"Protected failas: draudžiama keisti {path}")
        apply_write(path, f["content"], action)
        print(f"✓ Pritaikyta: {action} -> {path}")

    for cmd in plan.get("commands", []):
        rc = run_allowed(cmd)
        if rc != 0:
            raise RuntimeError(f"Komanda baigėsi klaida ({rc}): {cmd}")

    print("Viskas! Agentas baigė šį žingsnį.")
    if "notes" in plan:
        print("Pastabos:", plan["notes"])

if __name__ == "__main__":
    main()
