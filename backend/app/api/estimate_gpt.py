import os, json, logging, requests

log = logging.getLogger("estimate_gpt")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL_ANALYZE") or os.getenv("OPENAI_MODEL") or "gpt-4o-mini"

def _analyze_with_gpt(desc: str, locale: str):
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY missing")
    system = (
        "You are a cost-estimation API. Reply ONLY strict JSON with keys: "
        "materials (list of {name, unit, qty}), workflow (list of {task, hours}), "
        "crew (list of {role, count}), tools (list of {name, days}). "
        f"Locale={locale}. Avoid terraces; this is a garage with slab-on-ground when relevant."
    )
    url = "https://api.openai.com/v1/chat/completions"
    payload = {
        "model": MODEL,
        "messages": [
            {"role":"system","content":system},
            {"role":"user","content":desc}
        ],
        "response_format":{"type":"json_object"},
        "temperature":0,
        "seed": 1
    }
    r = requests.post(
        url,
        headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type":"application/json"},
        data=json.dumps(payload),
        timeout=60
    )
    r.raise_for_status()
    txt = r.json()["choices"][0]["message"]["content"]
    return json.loads(txt)
