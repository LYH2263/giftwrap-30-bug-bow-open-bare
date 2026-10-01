import pytest
from fastapi import HTTPException

from app.engines.wrap_math import ribbon_estimate
from app.repositories import history, settings_repo
from app.services import estimate_service

BOX_ID = 1  # 书型盒 0.30×0.20×0.15 clean

def test_off_equals_pre_change(tmp_db):
    """关闭时 ribbon_m 等于改造前同盒同捆扎结果。"""
    out = estimate_service.run_estimate(BOX_ID, None, "cross", False, 0.3, False, "")
    base = ribbon_estimate(0.30, 0.20, 0.15, "cross")
    assert out["ribbon"]["ribbon_m"] == base["ribbon_m"]
    assert out["ribbon"]["bow_enabled"] is False

def test_paper_never_moves_with_bow(tmp_db):
    """开启后 paper_m2 不随结长变化。"""
    off = estimate_service.run_estimate(BOX_ID, None, "cross", False, None, False, "")
    on_a = estimate_service.run_estimate(BOX_ID, None, "cross", True, 0.3, False, "")
    on_b = estimate_service.run_estimate(BOX_ID, None, "cross", True, 1.2, False, "")
    assert on_a["paper_m2"] == off["paper_m2"]
    assert on_b["paper_m2"] == off["paper_m2"]

def test_on_final_ribbon_is_base_plus_bow(tmp_db):
    out = estimate_service.run_estimate(BOX_ID, None, "cross", True, 0.3, False, "")
    base = ribbon_estimate(0.30, 0.20, 0.15, "cross")["ribbon_m"]
    assert out["ribbon"]["ribbon_m"] == round(base + 0.3, 2)

@pytest.mark.parametrize("bad", [0, -0.1])
def test_on_nonpositive_bow_fails_without_run(tmp_db, bad):
    """开启且结长≤0 失败且 calc_runs 不增加。"""
    before = history.count_runs()
    with pytest.raises(HTTPException) as ei:
        estimate_service.run_estimate(BOX_ID, None, "cross", True, bad, True, "")
    assert ei.value.status_code == 422
    assert history.count_runs() == before

def test_on_uses_setting_default_when_omitted(tmp_db):
    out = estimate_service.run_estimate(BOX_ID, None, "cross", True, None, False, "")
    assert out["ribbon"]["bow_m"] == settings_repo.get_bow_m()

def test_saved_run_contains_bow_fields(tmp_db):
    """落库须含 bow_enabled、bow_m、ribbon_m。"""
    r = estimate_service.run_estimate(BOX_ID, None, "cross", True, 0.35, True, "")
    run = history.get_run(r["run_id"])
    res = run["result"]
    assert res["bow_enabled"] is True
    assert res["bow_m"] == 0.35
    assert res["ribbon_m"] == r["ribbon"]["ribbon_m"]
    assert res["ribbon"]["ribbon_m"] == res["ribbon_m"]

def test_history_pinned_after_default_changes(tmp_db):
    """改丝带页默认结长后，用纸档摘要与详情的 ribbon_m 钉住写入值，不重算。"""
    r = estimate_service.run_estimate(BOX_ID, None, "cross", True, 0.3, True, "")
    saved_m = r["ribbon"]["ribbon_m"]
    saved_paper = r["paper_m2"]

    settings_repo.set_bow_m(0.9)  # 改默认结长

    detail = history.get_run(r["run_id"])["result"]
    summary = history.list_runs()[0]["result"]
    assert detail["ribbon_m"] == saved_m
    assert summary["ribbon_m"] == saved_m       # 摘要与详情彼此一致
    assert detail["paper_m2"] == saved_paper   # paper_m2 仍保持写入值
    assert detail["bow_m"] == 0.3

def test_detail_ribbon_keeps_bow_length(tmp_db):
    """回看详情：开关仍开启时，丝带必须仍是含结长的写入值，不许退回基础值。"""
    r = estimate_service.run_estimate(BOX_ID, None, "cross", True, 0.3, True, "")
    base = ribbon_estimate(0.30, 0.20, 0.15, "cross")["ribbon_m"]
    written = r["ribbon"]["ribbon_m"]
    assert written > base  # 开结米数必须高于关结同外形对照

    detail = history.get_run(r["run_id"])["result"]
    summary = history.list_runs()[0]["result"]
    # 开关/结长仍显示开启，丝带也必须是含结长的同一写入值
    assert detail["bow_enabled"] is True
    assert detail["bow_m"] == 0.3
    assert detail["ribbon_m"] == written
    assert detail["ribbon"]["ribbon_m"] == written
    assert detail["ribbon"]["base_ribbon_m"] == base
    # 列表与详情一致
    assert summary["ribbon_m"] == written
    assert summary["bow_enabled"] is True

def test_detail_off_ribbon_equals_base(tmp_db):
    """关结单详情丝带须等于改造前基础值，且不带任何结长。"""
    base = ribbon_estimate(0.30, 0.20, 0.15, "cross")["ribbon_m"]
    r = estimate_service.run_estimate(BOX_ID, None, "cross", False, 0.3, True, "")
    detail = history.get_run(r["run_id"])["result"]
    assert detail["bow_enabled"] is False
    assert detail["ribbon_m"] == base
    assert detail["ribbon"]["ribbon_m"] == base

def test_dry_rerun_cross_checks_history(tmp_db):
    """算纸台同参再干算丝带，须与回看（落库）互证。"""
    r = estimate_service.run_estimate(BOX_ID, 1.15, "cross", True, 0.4, True, "")
    again = estimate_service.run_estimate(BOX_ID, 1.15, "cross", True, 0.4, False, "")
    stored = history.get_run(r["run_id"])["result"]
    assert again["ribbon"]["ribbon_m"] == stored["ribbon_m"]
    assert again["paper_m2"] == stored["paper_m2"]
