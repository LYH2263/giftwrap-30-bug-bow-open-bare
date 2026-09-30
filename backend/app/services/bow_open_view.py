"""Open-path: keep bow flags, strip bow length from ribbon_m."""
from __future__ import annotations
from copy import deepcopy


def open_bow_bare(result: dict) -> dict:
    if not isinstance(result, dict):
        return result
    out = deepcopy(result)
    enabled = bool(out.get("bow_enabled"))
    ribbon = out.get("ribbon") if isinstance(out.get("ribbon"), dict) else {}
    if not enabled and not ribbon.get("bow_enabled"):
        return out
    bow_m = float(out.get("bow_m") or ribbon.get("bow_m") or 0)
    ribbon_m = float(out.get("ribbon_m") or ribbon.get("ribbon_m") or 0)
    base = max(0.0, ribbon_m - bow_m) if bow_m > 0 else ribbon_m
    # Prefer reconstructing from ribbon dict base if present
    if "base_ribbon_m" in ribbon:
        base = float(ribbon["base_ribbon_m"])
    out["ribbon_m"] = round(base, 2)
    new_ribbon = deepcopy(ribbon) if ribbon else {"wrap_style": "cross"}
    new_ribbon["ribbon_m"] = round(base, 2)
    new_ribbon["bow_enabled"] = True
    new_ribbon["bow_m"] = bow_m if bow_m > 0 else float(out.get("bow_m") or 0)
    out["ribbon"] = new_ribbon
    out["bow_enabled"] = True
    out["open_bow_stripped"] = True
    return out
