from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.repositories import settings_repo

router = APIRouter()

class BowSetting(BaseModel):
    bow_m: float

@router.get("/settings")
def settings(): return settings_repo.get_all()

@router.post("/settings/bow_m")
def set_bow_m(body: BowSetting):
    # 只改“默认结长”，历史用纸档是落库快照，不会被重算。
    if body.bow_m <= 0:
        raise HTTPException(422, "bow_m must be positive")
    settings_repo.set_bow_m(body.bow_m)
    return settings_repo.get_all()
