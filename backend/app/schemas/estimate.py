from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, conint, confloat

# --- Result schema ---


class Material(BaseModel):
    name: str
    # Priimam ir naują "qty", ir seną "quantity" per alias
    qty: confloat(gt=0) = Field(..., alias="quantity", description="Kiekis")
    # Leidžiami vienetai; neteisingi (pvz., "kg") turi kelti ValidationError
    unit: Literal["m", "m²", "m³", "vnt", "pcs"]
    # Priimam naują "unit_price_nok" ir seną "unit_price" per alias
    unit_price_nok: Optional[confloat(ge=0)] = Field(default=None, alias="unit_price")
    notes: Optional[str] = None

    # Pydantic v2 konfigūracija
    model_config = {
        "populate_by_name": True,  # leidžia pildyti pagal field name (ne tik alias)
        "extra": "allow",  # ignoruoja nenumatytus laukus iš senų testų
    }

    # Testų suderinamumui – senasis pavadinimas kaip property
    @property
    def unit_price(self) -> Optional[float]:
        return self.unit_price_nok


class WorkflowItem(BaseModel):
    step: conint(ge=1)
    task: str
    depends_on: Optional[List[int]] = None
    notes: Optional[str] = None


class WorkTimeItem(BaseModel):
    task: str
    hours: confloat(gt=0)


class CrewItem(BaseModel):
    role: str
    count: conint(ge=0)


class ToolItem(BaseModel):
    name: str
    duration_h: Optional[confloat(ge=0)] = None


class PricelistItem(BaseModel):
    source: Optional[str] = None
    ref: Optional[str] = None
    note: Optional[str] = None


class EstimateResult(BaseModel):
    materials: List[Material]
    workflow: List[WorkflowItem]
    work_time: List[WorkTimeItem]
    crew: List[CrewItem]
    tools: List[ToolItem]
    pricelists: List[PricelistItem]
    schema_version: str = "1.0.0"

    @classmethod
    def json_schema_str(cls) -> str:
        # JSON Schema tekstas promptui
        try:  # Pydantic v2
            return str(cls.model_json_schema())
        except Exception:  # Pydantic v1
            return cls.schema_json(indent=2)


# Kai kurie testai/legacy importai tikisi pavadinimo `EstimateResponse` — alias
class EstimateResponse(EstimateResult):
    pass


# --- Request schema expected by legacy tests/modules ---


class EstimateAnalyzeRequest(BaseModel):
    description: str
    custom_fields: Optional[Dict[str, Any]] = None


class EstimateUpdateRequest(BaseModel):
    # legacy pavadinimas testuose; turinys – visas EstimateResult
    result: EstimateResult


# --- Legacy alias names to satisfy older imports/tests ---


class AnalyzeRequest(EstimateAnalyzeRequest):
    pass


class AnalyzeResponse(EstimateResponse):
    pass


class UpdateRequest(EstimateUpdateRequest):
    pass


class UpdateResponse(EstimateResponse):
    pass
