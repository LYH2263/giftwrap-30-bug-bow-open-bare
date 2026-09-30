from fastapi.testclient import TestClient

from app.main import app
from app.repositories import history, settings_repo

def test_api_full_flow(tmp_db):
    c = TestClient(app)
    # 写入一单开启蝴蝶结
    r = c.post("/api/estimate", json={"box_id": 1, "wrap_style": "cross",
                                      "bow_enabled": True, "bow_m": 0.3, "save": True})
    assert r.status_code == 200
    body = r.json()
    run_id = body["run_id"]
    saved_m = body["ribbon"]["ribbon_m"]
    saved_paper = body["paper_m2"]

    # 开启且结长<=0：422（GET 试算与 POST 写入都拒绝），calc_runs 不增加
    before = history.count_runs()
    bad = c.post("/api/estimate", json={"box_id": 1, "bow_enabled": True, "bow_m": 0, "save": True})
    assert bad.status_code == 422
    assert history.count_runs() == before

    # 改默认结长后，详情接口仍返回写入快照
    settings_repo.set_bow_m(1.0)
    d = c.get(f"/api/runs/{run_id}").json()
    assert d["result"]["ribbon_m"] == saved_m
    assert d["result"]["paper_m2"] == saved_paper
    assert d["result"]["bow_m"] == 0.3

    # 列表摘要与详情一致
    s = c.get("/api/runs").json()["items"][0]
    assert s["result"]["ribbon_m"] == d["result"]["ribbon_m"]
    assert s["result"]["paper_m2"] == d["result"]["paper_m2"]

    # 同参干算与落库互证
    g = c.get("/api/estimate", params={"box_id": 1, "wrap_style": "cross",
                                       "bow_enabled": True, "bow_m": 0.3})
    assert g.json()["ribbon"]["ribbon_m"] == saved_m
    assert g.json()["paper_m2"] == saved_paper

def test_api_default_bow_setting(tmp_db):
    c = TestClient(app)
    r = c.post("/api/settings/bow_m", json={"bow_m": 0.45})
    assert r.status_code == 200 and float(r.json()["bow_m"]) == 0.45
    bad = c.post("/api/settings/bow_m", json={"bow_m": 0})
    assert bad.status_code == 422
