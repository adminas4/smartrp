from __future__ import annotations
import os, json, threading
from pathlib import Path
from typing import Literal

_Mode = Literal["demo","full"]
_LOCK = threading.Lock()
_PATH = Path("/var/lib/smartrp/mode.json")
_DEFAULT = os.getenv("OPENAI_MODE","demo").lower()

def _load_state() -> dict:
    try:
        if _PATH.exists():
            with _PATH.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and data.get("mode") in ("demo","full"):
                    return data
    except Exception:
        pass
    return {"mode": _DEFAULT if _DEFAULT in ("demo","full") else "demo"}

def _save_state(state: dict) -> None:
    _PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = _PATH.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(state, f)
    tmp.replace(_PATH)

def get_mode() -> _Mode:
    with _LOCK:
        return _load_state()["mode"]  # visada skaitom iš disko

def set_mode(mode: _Mode) -> None:
    if mode not in ("demo","full"):
        raise ValueError("mode must be 'demo' or 'full'")
    with _LOCK:
        _save_state({"mode": mode})

def is_full_mode() -> bool:
    return get_mode() == "full"
