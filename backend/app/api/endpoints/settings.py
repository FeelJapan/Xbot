from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.crud import settings as settings_crud
from app.schemas.settings import Settings

router = APIRouter()

@router.get("/settings", response_model=Settings)
def get_settings(
    db: Session = Depends(deps.get_db),
):
    """
    現在の設定を取得します。
    """
    db_settings = settings_crud.get_settings(db)
    if db_settings is None:
        raise HTTPException(status_code=404, detail="Settings not found")
    return settings_crud.convert_to_schema(db_settings)

@router.post("/settings", response_model=Settings)
def create_settings(
    settings: Settings,
    db: Session = Depends(deps.get_db),
):
    """
    新しい設定を作成します。
    """
    db_settings = settings_crud.create_settings(db, settings)
    return settings_crud.convert_to_schema(db_settings)

@router.put("/settings", response_model=Settings)
def update_settings(
    settings: Settings,
    db: Session = Depends(deps.get_db),
):
    """
    既存の設定を更新します。
    """
    db_settings = settings_crud.update_settings(db, settings)
    return settings_crud.convert_to_schema(db_settings) 