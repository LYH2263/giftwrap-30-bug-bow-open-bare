from fastapi import HTTPException
from app.engines.wrap_math import paper_area, ribbon_estimate
from app.modules.ribbon_bow import apply_bow
from app.repositories import boxes, history, settings_repo

def run_estimate(box_id: int, overlap: float | None, wrap_style: str,
                 bow_enabled: bool, bow_m: float | None, save: bool, note: str):
    box = boxes.get_box(box_id)
    if not box:
        raise HTTPException(404)
    if box.get("data_quality") == "dirty":
        raise HTTPException(422, "dirty box")
    # 开启且结长≤0 直接失败：在校验阶段拒绝，绝不进入落库，calc_runs 不增加。
    if bow_enabled:
        if bow_m is None:
            bow_m = settings_repo.get_bow_m()
        if float(bow_m) <= 0:
            raise HTTPException(422, "bow_m must be positive when bow_enabled")
    elif bow_m is None:
        bow_m = settings_repo.get_bow_m()

    ov = float(overlap) if overlap is not None else settings_repo.get_overlap()
    # 纸面积算法完全独立，结长不参与，paper_m2 不随蝴蝶结变化。
    calc = paper_area(box["length"], box["width"], box["height"], ov)
    base_ribbon = ribbon_estimate(box["length"], box["width"], box["height"], wrap_style)
    ribbon = apply_bow(base_ribbon, bow_enabled, float(bow_m))
    payload = {**calc, "ribbon": ribbon, "box_id": box_id,
               "bow_enabled": ribbon["bow_enabled"], "bow_m": ribbon["bow_m"],
               "ribbon_m": ribbon["ribbon_m"]}
    run_id = history.insert_run(box_id, ov, payload, note) if save else None
    return {"box": box, "run_id": run_id, **calc, "ribbon": ribbon}
