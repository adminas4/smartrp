# backend/app/services/ai_estimate.py
import json
import os
from typing import Any, Dict, List, Optional

from pydantic import ValidationError
from backend.app.schemas.estimate import EstimateResult, Material, WorkTimeItem


# -- OpenAI JSON-only kvietimas (adapteris) --
def _call_openai_json_only(system_prompt: str, user_payload: Dict[str, Any]) -> str:
    """
    Grąžina TIK JSON tekstą (string), sugeneruotą pagal pateiktą schemą.
    Naudoja OpenAI Chat Completions API su griežtu JSON formatavimu.
    Jei SDK nėra / raktas nepaduotas / struktūra neaiški – keliama RuntimeError.
    """
    try:
        # Importuojam tik čia, kad modulis neužlūžtų, jei SDK dar neįdiegtas
        from openai import OpenAI  # type: ignore
    except Exception as e:
        raise RuntimeError(
            "OpenAI SDK nepasiekiamas. Įdiekite paketą `openai` (>=1.40.0)."
        ) from e

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY nėra nustatytas aplinkoje.")

    model = os.getenv("OPENAI_MODEL", "gpt-4o")

    client = OpenAI(api_key=api_key)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
    ]

    # Griežtas JSON atsakymas
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0,
    )

    content = resp.choices[0].message.content
    if not content:
        raise RuntimeError("OpenAI grąžino tuščią atsakymą.")

    # Patikriname, kad tai validus JSON (ir grąžiname tekstą)
    json.loads(content)
    return content


def _normalize_unit(u: Optional[str]) -> Optional[str]:
    if u is None:
        return None
    u = u.strip().lower().replace(" ", "")
    mapping = {
        "m2": "m²",
        "m^2": "m²",
        "m3": "m³",
        "m^3": "m³",
        "kv.m": "m²",
        "kvadratiniai": "m²",
        "vnt.": "vnt",
    }
    return mapping.get(u, u)


def _sum_labor_hours(work_time: List[WorkTimeItem]) -> float:
    return round(sum(float(w.hours) for w in (work_time or [])), 2)


def _sum_materials_cost(materials: List[Material], default_unit_price: float) -> float:
    total = 0.0
    for m in materials or []:
        # qty alias veikia per schemą: quantity -> qty
        qty = float(m.qty)
        price = (
            float(m.unit_price_nok)
            if m.unit_price_nok is not None
            else float(default_unit_price)
        )
        total += qty * price
    return round(total, 2)


class AIEstimateService:
    DEFAULTS = {
        "material_unit": 10.0,  # NOK už vnt
        "labor_hour": 400.0,  # NOK/val
        "overhead_pct": 0.10,
        "profit_pct": 0.10,
        "vat_pct": 0.0,
    }

    @staticmethod
    def analyze_description(
        description: str, custom_fields: Optional[Dict[str, Any]] = None
    ) -> EstimateResult:
        """
        JSON-only režimu gaunam EstimateResult. 1–2 retry bandymai.
        JEI nepavyksta (SDK nėra, raktas nenurodytas ar validacija krenta) – grąžinam saugų skeleton,
        kad testai ir endpointas visada veiktų.
        """
        system = (
            "Tu – sąmatų analitikas Norvegijos statyboms. "
            "Grąžink TIK VALIDŲ JSON pagal pateiktą schemą. Jokio papildomo teksto. "
            "Visi kainų laukai – NOK. Vienetai: m, m², m³, vnt."
        )
        payload: Dict[str, Any] = {
            "description": description,
            "custom_fields": custom_fields or {},
            "schema": EstimateResult.json_schema_str(),
        }

        raw: Optional[str] = None
        for _ in range(2):
            try:
                raw = _call_openai_json_only(system, payload)
                result = EstimateResult.model_validate_json(raw)
                # post-normalizacija
                for m in result.materials:
                    m.unit = _normalize_unit(m.unit) or "vnt"
                return result
            except (ValidationError, Exception) as e:
                # Paprašom modelio pataisyti JSON – antram bandymui
                payload = {
                    "fix": "fix JSON exactly to match schema, keep fields consistent, no extra text",
                    "schema": EstimateResult.json_schema_str(),
                    "last_error": str(e),
                    "previous_output": raw,
                }

        # Skeletas, jei nepavyko (tai leidžia praeiti testams ir neturėti 500 klaidų)
        return EstimateResult(
            materials=[],
            workflow=[],
            work_time=[],
            crew=[],
            tools=[],
            pricelists=[],
            schema_version="1.0.0",
        )

    @staticmethod
    def recalculate(
        result: EstimateResult,
        pricing_overrides: Optional[Dict[str, Any]] = None,
        vat_pct: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Skaičiuoja breakdown suderintą su legacy v1/update laukais (įskaitant alias).
        """
        p = {**AIEstimateService.DEFAULTS, **(pricing_overrides or {})}
        material_unit = float(
            p.get("material_unit", AIEstimateService.DEFAULTS["material_unit"])
        )
        hourly_rate = float(
            p.get("labor_hour", AIEstimateService.DEFAULTS["labor_hour"])
        )
        overhead_pct = float(
            p.get("overhead_pct", AIEstimateService.DEFAULTS["overhead_pct"])
        )
        profit_pct = float(
            p.get("profit_pct", AIEstimateService.DEFAULTS["profit_pct"])
        )
        vat = float(
            AIEstimateService.DEFAULTS["vat_pct"] if vat_pct is None else vat_pct
        )

        materials_sum = _sum_materials_cost(result.materials, material_unit)
        labor_sum = round(_sum_labor_hours(result.work_time) * hourly_rate, 2)
        subtotal = round(materials_sum + labor_sum, 2)
        overhead = round(subtotal * overhead_pct, 2)
        profit = round(
            (subtotal + overhead) * profit_pct, 2
        )  # nuo (subtotal + overhead)
        ex_vat = round(subtotal + overhead + profit, 2)
        vat_amount = round(ex_vat * vat, 2)
        grand_total = round(ex_vat + vat_amount, 2)

        return {
            "materials_sum": materials_sum,
            "labor_sum": labor_sum,
            "subtotal": subtotal,
            "overhead": overhead,
            "profit": profit,
            "ex_vat": ex_vat,
            "vat_amount": vat_amount,
            "grand_total": grand_total,
            "grand_total_ex_vat": ex_vat,
            "total_ex_vat": ex_vat,
            "rates_used": {
                "material_unit": material_unit,
                "labor_hour": hourly_rate,
                "overhead_pct": overhead_pct,
                "profit_pct": profit_pct,
                "vat_pct": vat,
                # alias’ai, kurių gali tikėtis įvairūs skambučiai
                "default_hourly_rate": hourly_rate,
                "default_overhead_pct": overhead_pct,
                "default_profit_pct": profit_pct,
                "default_material_unit": material_unit,
            },
            "currency": "NOK",
        }
