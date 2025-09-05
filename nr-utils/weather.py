from __future__ import annotations
from typing import Any, Dict, List, Optional
from decimal import Decimal, InvalidOperation
from datetime import datetime

def _to_decimal(v: Any) -> Optional[Decimal]:
    if v is None or v == "":
        return None
    try:
        return Decimal(str(v))
    except (InvalidOperation, ValueError, TypeError):
        return None

def _parse_date(s: Any) -> Optional[str]:
    """Normalisiert Datum nach ISO-YYYY-MM-DD (falls möglich)."""
    if not s:
        return None
    if isinstance(s, datetime):
        return s.date().isoformat()
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S.%f"):
        try:
            return datetime.strptime(str(s), fmt).date().isoformat()
        except Exception:
            continue
    # Unverändert zurückgeben, wenn Format unbekannt – lieber roh als Verlust
    return str(s)

def format_days(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Normalisiert die Tageswerte in ein schlankes Schema:
      [{
        "date": "YYYY-MM-DD",
        "temp": float|None,
        "rain": float|None,
        "sun":  float|None,
        "relSun": float|None
      }, ...]
    """
    out: List[Dict[str, Any]] = []
    for r in rows or []:
        out.append({
            "date":   _parse_date(r.get("WeekDate") or r.get("Date")),
            "temp":   float(_to_decimal(r.get("Temperature") or r.get("Temp"))) if _to_decimal(r.get("Temperature") or r.get("Temp")) is not None else None,
            "rain":   float(_to_decimal(r.get("Rain") or r.get("Precip"))) if _to_decimal(r.get("Rain") or r.get("Precip")) is not None else None,
            "sun":    float(_to_decimal(r.get("TotalSunHours"))) if _to_decimal(r.get("TotalSunHours")) is not None else None,
            "relSun": float(_to_decimal(r.get("RelativeSunHours"))) if _to_decimal(r.get("RelativeSunHours")) is not None else None,
        })
    return out

def summarize(days: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Liefert einfache Aggregationen für LLM/Report:
      - avg_temp, sum_rain, sum_sun, days_count
    """
    temps = [d["temp"] for d in days if d.get("temp") is not None]
    rains = [d["rain"] for d in days if d.get("rain") is not None]
    suns  = [d["sun"]  for d in days if d.get("sun")  is not None]

    def _avg(xs: List[float]) -> Optional[float]:
        return round(sum(xs) / len(xs), 2) if xs else None

    return {
        "avg_temp": _avg(temps),
        "sum_rain": round(sum(rains), 1) if rains else None,
        "sum_sun":  round(sum(suns), 1)  if suns  else None,
        "days_count": len(days),
    }

def build_weather_payload(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Kombiniert Normalisierung + Summary:
      {
        "days": [...],
        "summary": {...}
      }
    """
    days = format_days(rows)
    return {"days": days, "summary": summarize(days)}
