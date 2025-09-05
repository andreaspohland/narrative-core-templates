from __future__ import annotations
from typing import Any, Dict, List, Optional, Iterable
from decimal import Decimal, InvalidOperation

Number = Optional[float]

def _to_decimal(v: Any) -> Optional[Decimal]:
    if v is None or v == "":
        return None
    try:
        return Decimal(str(v))
    except (InvalidOperation, ValueError, TypeError):
        return None

def _pct(n: Optional[Decimal], d: Optional[Decimal]) -> Optional[float]:
    if n is None or d is None or d == 0:
        return None
    try:
        return float(n / d)  # Anteil (0.2164 = 21.64 %)
    except Exception:
        return None

def _diff(cur: Optional[Decimal], py: Optional[Decimal]) -> Optional[float]:
    if cur is None or py is None:
        return None
    try:
        return float(cur - py)
    except Exception:
        return None

def _first(rows: List[Dict[str, Any]], key: str, value: Any) -> Optional[Dict[str, Any]]:
    for r in rows:
        if str(r.get(key, "")).upper() == str(value).upper():
            return r
    return None

def _coalesce_scope(rows: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Akzeptiert zwei gängige Formen:
    1) rows = [ {... "Scope":"WEEK"}, {... "Scope":"MTD"}, {... "Scope":"YTD"} ]
    2) rows = [ weekRow, mtdRow, ytdRow ]  (keine Scope-Spalte)
    """
    w = _first(rows, "Scope", "WEEK") or (rows[0] if rows else {})
    m = _first(rows, "Scope", "MTD")  or (rows[1] if len(rows) > 1 else {})
    y = _first(rows, "Scope", "YTD")  or (rows[2] if len(rows) > 2 else {})
    return {"week": w or {}, "mtd": m or {}, "ytd": y or {}}

def _ensure_metric_block(src: Dict[str, Any], base: str) -> Dict[str, Any]:
    """
    Stellt sicher: base, basePY, baseDiff, base_ChangePct (Anteil, nicht %)
    Falls Diff/ChangePct fehlen, werden sie berechnet.
    """
    cur = _to_decimal(src.get(base))
    py  = _to_decimal(src.get(f"{base}PY"))
    out = {
        base: float(cur) if cur is not None else None,
        f"{base}PY": float(py) if py is not None else None,
    }
    # Prefer vorhandene Felder, berechne sonst
    diff = src.get(f"{base}Diff")
    if diff is None:
        diff = _diff(cur, py)
    out[f"{base}Diff"] = diff

    chg = src.get(f"{base}_ChangePct")
    if chg is None:
        chg = _pct(cur - py if (cur is not None and py is not None) else None, py)
        # Klassisch wäre (cur-py)/py; einige Views liefern direkt cur/py.
        # Wir rechnen bewusst (cur - py) / py als Anteil.
    out[f"{base}_ChangePct"] = chg
    return out

def _merge_metrics(src: Dict[str, Any], metrics: Iterable[str]) -> Dict[str, Any]:
    out = {}
    for m in metrics:
        out.update(_ensure_metric_block(src, m))
    # Meta-Felder (Woche/Jahr) durchreichen, sofern vorhanden
    for meta in ["SalesWeekNr", "SalesYear", "SalesMonth", "SalesDate"]:
        if meta in src:
            out[meta] = src.get(meta)
    return out

def build_kpi(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Formt die KPI-View in das vom Template erwartete Objekt:
    {
      "week": {... NetAmount, NetAmountPY, NetAmountDiff, NetAmount_ChangePct, ...},
      "mtd":  {...},
      "ytd":  {...}
    }

    Unterstützte Spaltennamen (Beispiele):
      NetAmount, NetAmountPY, NetAmountDiff, NetAmount_ChangePct
      TransactionCnt, CustomerCnt, Quantity (+ jeweilige *_PY, *_Diff, *_ChangePct)
      SalesWeekNr, SalesYear

    Robust gegenüber fehlenden *_Diff / *_ChangePct: werden berechnet.
    """
    scopes = _coalesce_scope(rows or [])
    metrics = ["NetAmount", "TransactionCnt", "CustomerCnt", "Quantity"]

    week = _merge_metrics(scopes["week"], metrics)
    mtd  = _merge_metrics(scopes["mtd"],  metrics)
    ytd  = _merge_metrics(scopes["ytd"],  metrics)

    return {
        "week": week,
        "mtd":  mtd,
        "ytd":  ytd,
    }
