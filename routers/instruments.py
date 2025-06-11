from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
from db import get_db
from oauth2 import get_current_user

router = APIRouter(
    prefix="/instruments",
    tags=["Instruments"]
)

# Utility: Admin check
def require_admin(user: models.User):
    if user.privilege_level != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins are allowed to perform this action"
        )

# --------- CREATE INSTRUMENT (ADMIN ONLY) ---------
@router.post("/", response_model=schemas.Instrument)
def create_instrument(
    instrument: schemas.InstrumentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    require_admin(current_user)

    db_instrument = models.Instrument(**instrument.dict())
    db.add(db_instrument)
    db.commit()
    db.refresh(db_instrument)
    return db_instrument


# --------- GET ALL INSTRUMENTS (PUBLIC) ---------
@router.get("/", response_model=List[schemas.Instrument])
def get_instruments(db: Session = Depends(get_db)):
    return db.query(models.Instrument).all()


# --------- UPDATE INSTRUMENT (ADMIN ONLY) ---------
@router.put("/{instrument_id}", response_model=schemas.Instrument)
def update_instrument(
    instrument_id: int,
    updated: schemas.InstrumentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    require_admin(current_user)

    instrument = db.query(models.Instrument).filter(models.Instrument.instrument_id == instrument_id).first()
    if not instrument:
        raise HTTPException(status_code=404, detail="Instrument not found")

    for key, value in updated.dict().items():
        setattr(instrument, key, value)

    db.commit()
    db.refresh(instrument)
    return instrument


# --------- DELETE INSTRUMENT (ADMIN ONLY) ---------
@router.delete("/{instrument_id}")
def delete_instrument(
    instrument_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    require_admin(current_user)

    instrument = db.query(models.Instrument).filter(models.Instrument.instrument_id == instrument_id).first()
    if not instrument:
        raise HTTPException(status_code=404, detail="Instrument not found")

    db.delete(instrument)
    db.commit()
    return {"message": "Instrument deleted successfully"}
