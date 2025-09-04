import re
LT = re.compile(r"[ąčęėįšųūžĄČĘĖĮŠŲŪŽ]")

UNITS = {
    "vnt":"stk","vnt.":"stk","m2":"m²","kv.m":"m²","kv.m.":"m²",
    "m3":"m³","kg":"kg","m":"m","stk":"stk"
}

def normalize_units(u: str) -> str:
    return UNITS.get(u.strip(), u.strip())

def assert_norwegian_payload(payload: dict):
    s = str(payload)
    if LT.search(s):
        raise ValueError("Payload contains non-NO characters")
    return payload
