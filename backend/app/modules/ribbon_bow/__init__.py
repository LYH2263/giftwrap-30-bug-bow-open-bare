"""蝴蝶结加长丝带模块。

只加在丝带上，绝不触碰纸面积。
- 关闭(bow_enabled=False): ribbon_m 等于改造前的同盒同捆扎结果。
- 开启(bow_enabled=True):  最终 ribbon_m = 原 ribbon_m + bow_m（结长，米）。
"""

from app.config import DEFAULT_BOW_M

def apply_bow(base_ribbon: dict, bow_enabled: bool, bow_m: float) -> dict:
    """在基础捆扎丝带结果上叠加蝴蝶结结长。

    base_ribbon 必须含 ribbon_m；返回 dict 始终带 bow_enabled / bow_m。
    仅修改丝带字段，paper_m2 不参与计算，也不出现在返回里。
    """
    base_m = float(base_ribbon["ribbon_m"])
    if bow_enabled:
        bow_m = float(bow_m)
        total = base_m + bow_m
    else:
        bow_m = float(bow_m)
        total = base_m
    return {
        **base_ribbon,
        "ribbon_m": round(total, 2),
        "base_ribbon_m": round(base_m, 2),
        "bow_enabled": bool(bow_enabled),
        "bow_m": round(bow_m, 3),
    }
