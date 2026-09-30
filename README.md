# 20-giftwrap（礼品包装纸）

Giftwrap — 盒体展开近似面积（含重叠余量系数）

## 启动

```bash
docker compose up --build
```

| 入口 | 地址 |
| --- | --- |
| 前端 | http://localhost:4900 |
| API | http://localhost:9900 |

## 主链

盒长宽高 → 包装纸面积 → 展开示意

## 蝴蝶结加长丝带

- `bow_enabled=false`：`ribbon_m` 等于改造前同盒同捆扎结果，`paper_m2` 完全不动。
- `bow_enabled=true`：最终丝带 = 原 `ribbon_m` + `bow_m`（结长，米）；`paper_m2` 不随结长变化。
- 开启且 `bow_m ≤ 0` 返回 422，`calc_runs` 不增加。
- 落库快照含 `bow_enabled`、`bow_m`、`ribbon_m`；用纸档列表与详情只从落库读取，改默认结长（`POST /api/settings/bow_m`）不会重算历史。

接口：`GET/POST /api/estimate`（参数 `box_id, overlap?, wrap_style, bow_enabled, bow_m?, save, note?`），
回看 `GET /api/runs`、`GET /api/runs/{id}`。

## 技术栈

Python 3.12 + FastAPI + SQLite；Vue 3 + Vite + Nginx。
