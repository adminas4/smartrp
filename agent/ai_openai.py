import os
import json
from typing import Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential

try:
    from openai import OpenAI
except Exception as e:
    raise RuntimeError("OpenAI SDK nerasta. Įdiek: pip install openai") from e

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    raise RuntimeError("Nerastas OPENAI_API_KEY aplinkos kintamasis (.env faile).")

client = OpenAI(api_key=API_KEY)

# GRIEŽTAS JSON-ONLY SYSTEM PROMPT
SYSTEM_PROMPT = """Tu esi vyresnysis programinės įrangos inžinierius-agentas.
Tavo užduotis: kurti ir keisti SmartRP sąmatos modulio failus bei siūlyti paleidimo komandas.

GRĄŽINK TIK GRYNĄ JSON (be jokio papildomo teksto, be ``` blokų), tik tokios formos:
{
  "files": [
    { "path": "relative/path/from/repo/root", "action": "write", "content": "<PILNAS failo turinys>" }
  ],
  "commands": ["pytest -q"],
  "notes": "trumpi paaiškinimai (nebūtina)"
}

TAISYKLĖS:
- GRĄŽINK TIK VIENĄ JSON OBJEKTĄ. JOKIŲ paaiškinimų už JSON ribų.
- 'files[*].action' visada 'write' (VENK 'append' ar 'patch').
- Rašyti leidžiama TIK whiteliste nurodytuose kataloguose.
- 'content' turi būti PILNAS failo turinys, paruoštas įrašymui.
- Jei kuri API maršrutus FastAPI, naudok esamą paketų struktūrą (pvz., 'from backend.app ...').
- Valiuta visur: NOK.
- Jei siūlai testus, naudok pytest; komandas rinkis tik iš leistinų ('allowed_commands').
- Jei negali įvykdyti užduoties, grąžink JSON su {"files":[], "commands":[], "notes":"klaidos ar priežasties paaiškinimas"}.
"""

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=8))
def ask_agent(goal: str, context: str) -> Dict[str, Any]:
    """
    Naudojam Chat Completions API, nes ši aplinka neturi client.responses.
    Bandome paprašyti JSON formatu; jeigu modelis vis tiek įterpia pašalinį tekstą,
    iškerpam JSON nuo pirmos '{' iki paskutinės '}' ir bandome parse'inti.
    """
    # Bandysim naudoti JSON režimą, jei modelis jį palaiko
    response = client.chat.completions.create(
        model=MODEL,
        temperature=float(os.getenv("AGENT_TEMP", "0.2")),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Tikslas:\n{goal}\n\nKontekstas:\n{context}"},
        ],
        # JSON režimas (jei modelis nepalaiko, OpenAI tiesiog ignoruos)
        response_format={"type": "json_object"},
    )

    # Ištraukiam tekstą
    content = (response.choices[0].message.content or "").strip()
    if not content:
        raise RuntimeError("Modelis negrąžino jokio teksto.")

    # Iškerpam tik JSON dalį (saugiklis, jei vistiek kažką pridėjo)
    start_idx = content.find("{")
    end_idx = content.rfind("}")
    json_text = content[start_idx:end_idx + 1] if (start_idx != -1 and end_idx != -1) else content

    try:
        return json.loads(json_text)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Negalima išparsinti JSON. Gauta:\n{content}\nKlaida: {e}")
