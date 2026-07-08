from django.utils.dateparse import parse_date, parse_datetime

NAME_USE_PRIORITY = {"official": 0, "usual": 1}


def _pick_name_entry(names: list) -> dict:
    return min(names, key=lambda n: NAME_USE_PRIORITY.get(n.get("use"), 99))


def _format_name(entry: dict) -> str:
    given = " ".join(entry.get("given", []))
    family = entry.get("family", "")
    full = " ".join(part for part in [given, family] if part)
    return full or "Unknown"


def patient_fields_from_fhir(resource: dict) -> dict:
    names = resource.get("name") or []
    name = _format_name(_pick_name_entry(names)) if names else "Unknown"

    birth_date = None
    if resource.get("birthDate"):
        birth_date = parse_date(resource["birthDate"])

    return {
        "name": name,
        "gender": resource.get("gender", ""),
        "birth_date": birth_date,
    }


def _value_text_from_observation(resource: dict) -> str:
    if "valueQuantity" in resource:
        vq = resource["valueQuantity"]
        value = vq.get("value")
        unit = vq.get("unit", "")
        if value is None:
            return ""
        return f"{value} {unit}".strip()
    if "valueString" in resource:
        return resource["valueString"]
    if "valueCodeableConcept" in resource:
        concept = resource["valueCodeableConcept"]
        if concept.get("text"):
            return concept["text"]
        codings = concept.get("coding") or []
        if codings:
            return codings[0].get("display", codings[0].get("code", ""))
        return ""
    return ""


def observation_fields_from_fhir(resource: dict) -> dict:

    code = resource.get("code") or {}
    code_text = code.get("text")
    if not code_text:
        codings = code.get("coding") or []
        if codings:
            code_text = codings[0].get("display") or codings[0].get("code")
    code_text = code_text or "Unknown"

    effective_date = None
    if resource.get("effectiveDateTime"):
        effective_date = parse_datetime(resource["effectiveDateTime"])
    elif resource.get("effectivePeriod", {}).get("start"):
        effective_date = parse_datetime(resource["effectivePeriod"]["start"])

    return {
        "code_text": code_text,
        "value_text": _value_text_from_observation(resource),
        "effective_date": effective_date,
        "status": resource.get("status", ""),
    }
