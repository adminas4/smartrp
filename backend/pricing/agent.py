import json
from typing import Optional, List, Dict, Any
import asyncio, re
from urllib.parse import quote_plus, urljoin, urlparse
import httpx, yaml
from bs4 import BeautifulSoup

# Norvegiškos antraštės
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36",
    "Accept-Language": "nb-NO,nb;q=0.9,no;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# „kr“, „NOK“, „,-“ ir tūkst. tarpai
_PRICE_RE = re.compile(r'(?<!\d)(\d{2,3}(?:[ \u00A0]?\d{3})*)(?:\s*(?:kr|,-|NOK))\b', re.I)

def load_whitelist(path: str = '/srv/smartrp/backend/pricing/whitelist.yaml') -> List[str]:
    try:
        data = yaml.safe_load(open(path, 'r'))
        return [d.strip() for d in data if isinstance(d, str) and d.strip()]
    except Exception:
        return [
            'elektroimportoren.no','megaflis.no','bygghjemme.no','maxbo.no',
            'monter.no','byggmakker.no','byggern.no','prisjakt.no'
        ]

def _normalize_price(txt: str) -> Optional[int]:
    digits = re.sub(r'[^\d]', '', txt or '')
    return int(digits) if digits else None

def _extract_price_nok(html: str) -> Optional[int]:
    from bs4 import BeautifulSoup
    if not html: return None
    soup = BeautifulSoup(html, 'html.parser')

    # 1) JSON-LD su NOK
    for tag in soup.find_all('script', type='application/ld+json'):
        try:
            data = json.loads(tag.string or '' )
        except Exception:
            data = None
        def walk(x):
            if isinstance(x, dict):
                cur = x.get('priceCurrency') or x.get('priceCurrency')
                amt = x.get('price') or x.get('lowPrice') or x.get('highPrice')
                if (str(cur) or '' ).upper() == 'NOK' and amt:
                    try:
                        return int(str(amt).replace(' ', ''))
                    except Exception:
                        pass
                for v in x.values():
                    r = walk(v)
                    if r: return r
            elif isinstance(x, list):
                for v in x:
                    r = walk(v)
                    if r: return r
            return None
        if data:
            r = walk(data)
            if r: return r

    # 2) Matomas tekstas (be script/style)
    text = ' '.join(soup.stripped_strings)
    # leiskime tik reikšmes su kr/NOK ir (pageidautina) su žodžiu pris šalia
    for m in _PRICE_RE.finditer(text):
        val = _normalize_price(m.group(1))
        if not val: continue
        # Greiti filtrai nuo promo: įprastos ribos
        if not (5 <= val <= 200000):
            continue
        # kontekstas aplink skaičių
        s = text[max(0, m.start()-20): m.end()+20].lower()
        if 'kr' in s or 'nok' in s or 'pris' in s:
            return val
    return None
