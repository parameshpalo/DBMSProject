from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
from db import get_db  # Assumes you have a `get_db` function in db.py

router = APIRouter(
    prefix="/instruments",
    tags=["Instruments"]
)

# --------- CREATE INSTRUMENT ---------
@router.post("/", response_model=schemas.Instrument)
def create_instrument(instrument: schemas.InstrumentCreate, db: Session = Depends(get_db)):
    db_instrument = models.Instrument(**instrument.dict())
    db.add(db_instrument)
    db.commit()
    db.refresh(db_instrument)
    return db_instrument


# --------- GET ALL INSTRUMENTS ---------
@router.get("/", response_model=List[schemas.Instrument])
def get_instruments(db: Session = Depends(get_db)):
    return db.query(models.Instrument).all()


# --------- UPDATE INSTRUMENT ---------
@router.put("/{instrument_id}", response_model=schemas.Instrument)
def update_instrument(instrument_id: int, updated: schemas.InstrumentCreate, db: Session = Depends(get_db)):
    instrument = db.query(models.Instrument).filter(models.Instrument.instrument_id == instrument_id).first()
    if not instrument:
        raise HTTPException(status_code=404, detail="Instrument not found")

    for key, value in updated.dict().items():
        setattr(instrument, key, value)

    db.commit()
    db.refresh(instrument)
    return instrument


# --------- DELETE INSTRUMENT ---------
@router.delete("/{instrument_id}")
def delete_instrument(instrument_id: int, db: Session = Depends(get_db)):
    instrument = db.query(models.Instrument).filter(models.Instrument.instrument_id == instrument_id).first()
    if not instrument:
        raise HTTPException(status_code=404, detail="Instrument not found")

    db.delete(instrument)
    db.commit()
    return {"message": "Instrument deleted successfully"}
