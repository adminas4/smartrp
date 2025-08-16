# backend/app/services/config.py
import json
import os
from pathlib import Path
from typing import Dict

# Numatyti (fallback) nustatymai, jei nėra konfigo failo
DEFAULTS: Dict[str, float] = {
    "default_hourly_rate": 500.0,
    "default_overhead_pct": 0.10,
    "default_profit_pct": 0.10,
    "default_vat_pct": 0.25,
}

def _try_load_json(path: Path) -> Dict:
    try:
        if path.is_file():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        # Sugadintas failas – grįžtam prie DEFAULTS
        pass
    return {}

def load_base_config() -> Dict:
    """
    Skaitymo prioritetas:
    1) ENV kintamasis SMARTRP_CONFIG (pilnas kelias iki JSON)
    2) repo 'config/base.json'
    3) /etc/smartrp/base.json
    4) DEFAULTS
    """
    candidates = []

    env_path = os.getenv("SMARTRP_CONFIG")
    if env_path:
        candidates.append(Path(env_path))

    candidates.append(Path("config/base.json"))
    candidates.append(Path("/etc/smartrp/base.json"))

    cfg = DEFAULTS.copy()
    for p in candidates:
        cfg.update(_try_load_json(p))

    # Minimalus „sanity check“ (apsauga nuo neigiamų/keistų reikšmių)
    if cfg.get("default_hourly_rate", 0) < 0:
        cfg["default_hourly_rate"] = DEFAULTS["default_hourly_rate"]
    for pct_key in ("default_overhead_pct", "default_profit_pct", "default_vat_pct"):
        v = cfg.get(pct_key, DEFAULTS[pct_key])
        if not (0.0 <= float(v) <= 1.0):
            cfg[pct_key] = DEFAULTS[pct_key]

    return cfg
