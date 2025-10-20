
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import json, os, re, time
from pathlib import Path

APP_TITLE = "RooferBot API"
VERSION = "1.2-bilingual"

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = Path(os.getenv("RB_CONFIG", BASE_DIR / "config.example.json"))
DATA_DIR = BASE_DIR / "data"
LEADS_PATH = DATA_DIR / "leads.json"

app = FastAPI(title=APP_TITLE, version=VERSION)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load config
if not CONFIG_PATH.exists():
    raise RuntimeError(f"Config not found at {CONFIG_PATH}")
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CFG = json.load(f)

LANGS = ("de", "en")

def pick_lang(text: str = "", header_lang: str = "", explicit: str = "") -> str:
    # precedence: explicit from client -> accept-language -> text heuristic -> default de
    if explicit in LANGS:
        return explicit
    if header_lang:
        h = header_lang.lower()
        if h.startswith("de"): return "de"
        if h.startswith("en"): return "en"
    t = (text or "").lower()
    if re.search(r"[äöüß]|(und|bitte|dach|angebot|sturm|leck)", t):
        return "de"
    if re.search(r"(and|please|roof|quote|storm|leak)", t):
        return "en"
    return CFG.get("defaults", {}).get("lang", "de")

MATERIAL_MAP = {
    "de": {
        "ziegel": (75, 120),
        "beton": (65, 105),
        "schiefer": (140, 220),
        "metall": (90, 150),
    },
    "en": {
        "tile": (75, 120),
        "concrete": (65, 105),
        "slate": (140, 220),
        "metal": (90, 150),
    },
}

COMPLEXITY_FACTOR = {"simple":1.0, "einfach":1.0, "mittel":1.2, "medium":1.2, "komplex":1.5, "complex":1.5}

def estimate(area_m2: float, material_key: str, lang: str, complexity: str = "mittel") -> str:
    mm = MATERIAL_MAP["de"] if lang == "de" else MATERIAL_MAP["en"]
    low, high = mm.get(material_key, (70, 120))
    factor = COMPLEXITY_FACTOR.get(complexity, 1.2)
    lo = int(area_m2 * low * factor)
    hi = int(area_m2 * high * factor)
    if lang == "de":
        return f"Unverbindliche Schätzung: {lo:,}–{hi:,} € (netto)".replace(",", ".")
    return f"Rough estimate: €{lo:,}–€{hi:,} (excl. VAT)".replace(",", ".")

def load_faq(lang: str) -> Dict[str, str]:
    block = CFG.get("faq", {}).get(lang, {})
    return {k.lower(): v for k, v in block.items()}

class ChatIn(BaseModel):
    sid: str
    text: str
    meta: Optional[dict] = None  # may include lang, url, ua

class ChatOut(BaseModel):
    messages: List[str]
    cta: Optional[Dict] = None

class Lead(BaseModel):
    ts: float
    sid: str
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    zip: Optional[str] = None
    area_m2: Optional[float] = None
    material: Optional[str] = None
    issue: Optional[str] = None
    source_url: Optional[str] = None
    lang: Optional[str] = None

DATA_DIR.mkdir(exist_ok=True)
if not LEADS_PATH.exists():
    LEADS_PATH.write_text("[]", encoding="utf-8")

@app.get("/health")
def health():
    return {"ok": True, "version": VERSION}

def intent(text: str, lang: str) -> str:
    t = (text or "").lower()
    if lang == "de":
        if any(k in t for k in ["sturm", "sturmschaden", "notfall", "leck", "tropf", "eilt"]): return "notfall"
        if any(k in t for k in ["angebot", "preis", "kosten", "schätzung"]): return "angebot"
        if any(k in t for k in ["termin", "besichtigung", "beratung", "rückruf"]): return "termin"
        if any(k in t for k in ["pv", "photovoltaik", "solar"]): return "pv"
    else:
        if any(k in t for k in ["storm", "emergency", "leak", "urgent"]): return "notfall"
        if any(k in t for k in ["quote", "price", "cost", "estimate"]): return "angebot"
        if any(k in t for k in ["appointment", "site visit", "consult", "call back", "callback"]): return "termin"
        if any(k in t for k in ["pv", "solar", "photovoltaic"]): return "pv"
    # FAQ fuzzy
    FAQ = load_faq(lang)
    for q in FAQ.keys():
        parts = q.split()
        if len(parts) >= 2 and all(w in t for w in parts[:2]):
            return "faq"
    return "smalltalk"

@app.post("/chat", response_model=ChatOut)
async def chat(inp: ChatIn, request: Request):
    header_lang = request.headers.get("accept-language", "")
    explicit = (inp.meta or {}).get("lang", "")
    lang = pick_lang(inp.text, header_lang, explicit)

    FAQ = load_faq(lang)
    t = inp.text.strip()

    if lang == "de":
        msgs_notfall = [
            "Es tut mir leid zu hören, dass Sie einen Schaden haben.",
            "Bitte nennen Sie kurz: Adresse/PLZ, Schadensart (z. B. Sturmschaden/Leck), ca. m² und Ihre Telefonnummer.",
            "Wir priorisieren Notfälle – auf Wunsch Rückruf in 30 Min (Mo–Fr, 8–18 Uhr).",
        ]
        msg_termin = "Gern – eine Vor-Ort-Besichtigung ist meist sinnvoll."
        fallback1 = "Worum geht es – Sturmschaden, Dachsanierung, Photovoltaik oder Termin?"
        fallback2 = "Sie können auch gleich m²-Angabe & Material nennen (z. B. ‚120 m² Ziegel‘)."
    else:
        msgs_notfall = [
            "Sorry to hear about the damage.",
            "Please share: address/ZIP, type of issue (e.g., storm damage/leak), approx. area (m²) and your phone number.",
            "Emergencies are prioritized – optional call-back within 30 minutes (Mon–Fri, 8am–6pm).",
        ]
        msg_termin = "Sure — a site visit usually makes sense."
        fallback1 = "What do you need — storm damage, re-roofing, solar PV, or an appointment?"
        fallback2 = "You can also send size & material (e.g., '120 m² tile')."

    i = intent(t, lang)

    if i == "notfall":
        return ChatOut(messages=msgs_notfall)

    if i == "termin":
        cal = CFG.get("calendar_url") or ""
        cta = {"label": "Termin buchen" if lang == "de" else "Book appointment", "url": cal} if cal else None
        return ChatOut(messages=[msg_termin], cta=cta)

    if i == "angebot":
        text_norm = t.replace("²", "2")
        m = re.search(r"(\d{2,4})\s*m", text_norm)
        area = float(m.group(1)) if m else float(CFG.get("defaults", {}).get("area_m2", 120))
        if lang == "de":
            mat_key = "ziegel"
            for k in MATERIAL_MAP["de"].keys():
                if k in text_norm: mat_key = k; break
        else:
            mat_key = "tile"
            for k in MATERIAL_MAP["en"].keys():
                if k in text_norm: mat_key = k; break
        est = estimate(area, mat_key, lang, "mittel")
        if lang == "de":
            msg = f"{est}\nMaterial: {mat_key.title()}, Fläche: {int(area)} m².\nHinweis: Finale Kalkulation nach Besichtigung."
        else:
            msg = f"{est}\nMaterial: {mat_key.title()}, Area: {int(area)} m².\nNote: Final quote after site visit."
        return ChatOut(messages=[msg])

    if i == "pv":
        pv_text = CFG.get("snippets", {}).get(lang, {}).get("pv", "")
        return ChatOut(messages=[pv_text or ("PV possible; check structure, orientation and penetrations." if lang=="en" else "PV meist möglich; Statik, Ausrichtung und Durchdringungen beachten.")])

    if i == "faq" and FAQ:
        best_q = max(FAQ.keys(), key=lambda q: sum(w in t.lower() for w in q.split()))
        return ChatOut(messages=[FAQ[best_q]])

    return ChatOut(messages=[fallback1, fallback2])

@app.post("/lead")
def submit_lead(lead: Lead):
    lead.ts = time.time()
    try:
        db = json.loads(LEADS_PATH.read_text(encoding="utf-8"))
    except Exception:
        db = []
    db.append(lead.dict())
    LEADS_PATH.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"ok": True}
