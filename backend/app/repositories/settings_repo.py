from app.config import DEFAULT_OVERLAP, DEFAULT_BOW_M
from app.db import connect

def get_all():
    c = connect()
    try:
        d = {r["key"]: r["value"] for r in c.execute("SELECT key,value FROM settings").fetchall()}
        d.setdefault("overlap", str(DEFAULT_OVERLAP))
        d.setdefault("bow_m", str(DEFAULT_BOW_M))
        return d
    finally:
        c.close()

def get_overlap():
    return float(get_all().get("overlap", DEFAULT_OVERLAP))

def get_bow_m():
    return float(get_all().get("bow_m", DEFAULT_BOW_M))

def set_bow_m(value: float):
    c = connect()
    try:
        c.execute(
            "INSERT INTO settings(key,value) VALUES ('bow_m',?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (str(float(value)),),
        )
        c.commit()
    finally:
        c.close()
