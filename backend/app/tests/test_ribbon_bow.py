from app.engines.wrap_math import ribbon_estimate
from app.modules.ribbon_bow import apply_bow, DEFAULT_BOW_M

def test_off_keeps_base_ribbon():
    base = ribbon_estimate(0.30, 0.20, 0.15, "cross")
    out = apply_bow(base, False, DEFAULT_BOW_M)
    assert out["ribbon_m"] == base["ribbon_m"]
    assert out["bow_enabled"] is False
    assert out["bow_m"] == DEFAULT_BOW_M
    assert "paper_m2" not in out  # 结长模块绝不触碰纸面积

def test_on_adds_bow_length():
    base = ribbon_estimate(0.30, 0.20, 0.15, "cross")
    out = apply_bow(base, True, 0.3)
    assert out["ribbon_m"] == round(base["ribbon_m"] + 0.3, 2)
    assert out["bow_enabled"] is True
    assert out["base_ribbon_m"] == base["ribbon_m"]

def test_band_style_unchanged_then_added():
    base = ribbon_estimate(0.30, 0.20, 0.15, "band")
    assert apply_bow(base, False, 0.4)["ribbon_m"] == base["ribbon_m"]
    assert apply_bow(base, True, 0.4)["ribbon_m"] == round(base["ribbon_m"] + 0.4, 2)
