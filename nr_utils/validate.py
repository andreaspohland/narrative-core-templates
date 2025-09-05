from __future__ import annotations
from typing import Any, Dict
import json

try:
    import jsonschema
except ImportError:
    jsonschema = None

def validate_json(payload: Dict[str, Any], schema: Dict[str, Any]) -> None:
    """
    Validiert payload gegen JSON-Schema (optional, wenn jsonschema installiert).
    Raises jsonschema.ValidationError bei Verstößen.
    """
    if jsonschema is None:
        return
    jsonschema.validate(instance=payload, schema=schema)
