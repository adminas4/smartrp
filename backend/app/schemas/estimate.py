from typing import List, Optional, Dict, Literal
from pydantic import BaseModel, field_validator, conint


# --- Esami modeliai (su validacija) ---

class Material(BaseModel):
    name: str
    quantity: conint(ge=0)  # kiekis >= 0
    # pasirenkami laukai: vienetai ir vieneto kaina (jei kada reikės)
    unit: Optional[Literal["pcs", "m2", "m3", "m"]] = None
    unit_price: Optional[float] = None

    @field_validator("unit_price")
    @classmethod
    def _non_negative_unit_price(cls, v):
        if v is None:
            return v
        if v < 0:
            raise ValueError("unit_price negali būti neigiamas")
        return v


class Workflow(BaseModel):
    task: str
    hours: conint(ge=0)  # valandos >= 0


class EstimateResponse(BaseModel):
    currency: str
    materials: List[Material]
    workflow: List[Workflow]


# --- Tarifų override'ai ---

class PricingOverrides(BaseModel):
    material_unit: Optional[float] = None      # NOK / vnt
    labor_hour: Optional[float] = None         # NOK / h
    overhead_pct: Optional[float] = None       # 0..1
    profit_pct: Optional[float] = None         # 0..1

    @field_validator("material_unit", "labor_hour")
    @classmethod
    def _non_negative(cls, v):
        if v is None:
            return v
        if v < 0:
            raise ValueError("Kainos negali būti neigiamos")
        return v

    @field_validator("overhead_pct", "profit_pct")
    @classmethod
    def _pct_range(cls, v):
        if v is None:
            return v
        if not (0.0 <= v <= 1.0):
            raise ValueError("Procentai turi būti tarp 0.0 ir 1.0")
        return v


class UpdateRequest(BaseModel):
    materials: List[Material]
    workflow: List[Workflow]
    # pasirenkamas PVM, numatyta 25% (0.25). Galima siųsti 0..1
    vat_pct: Optional[float] = 0.25
    # override'ai (pasirenkami)
    pricing: Optional[PricingOverrides] = None
    # pasirenkamas profilio pavadinimas (jei naudosim profilius ateityje)
    pricing_profile: Optional[str] = None

    @field_validator("vat_pct")
    @classmethod
    def _vat_range(cls, v):
        if v is None:
            return v
        if not (0.0 <= v <= 1.0):
            raise ValueError("vat_pct turi būti tarp 0.0 ir 1.0")
        return v


class UpdateResponse(BaseModel):
    currency: str
    totals: float  # suderinamumui su esamais testais

    # detalizuotas išskaidymas (nebūtini laukai)
    materials_sum: Optional[float] = None
    labor_sum: Optional[float] = None
    overhead: Optional[float] = None
    profit: Optional[float] = None

    # prieš PVM ir po PVM
    grand_total_ex_vat: Optional[float] = None
    vat_pct: Optional[float] = None
    vat_amount: Optional[float] = None
    grand_total: Optional[float] = None  # po PVM

    # metaduomenys
    schema_version: Optional[str] = None
    calc_id: Optional[str] = None
    timestamp: Optional[int] = None
    warnings: Optional[List[str]] = None
    rates_used: Optional[Dict[str, float]] = None


# --- Nauji modeliai POST /estimate/analyze įvedimui ---

class EstimateAnalyzeRequest(BaseModel):
    description: str
    custom_fields: Optional[Dict[str, str]] = None
    currency: str = "NOK"  # numatyta valiuta


class AnalyzeMeta(BaseModel):
    source: str = "mock"
