from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import models, schemas
from db import get_db

router = APIRouter(
    prefix="/labs",
    tags=["Labs"]
)

# --------- CREATE LAB ---------
@router.post("/", response_model=schemas.Lab)
def create_lab(lab: schemas.LabCreate, db: Session = Depends(get_db)):
    db_lab = models.Labs(**lab.dict())
    db.add(db_lab)
    db.commit()
    db.refresh(db_lab)
    return db_lab

# --------- GET ALL LABS ---------
@router.get("/", response_model=List[schemas.Lab])
def get_all_labs(db: Session = Depends(get_db)):
    return db.query(models.Labs).all()

# --------- GET INSTRUMENTS IN A LAB ---------
@router.get("/{lab_id}/instruments", response_model=List[schemas.Instrument])
def get_instruments_in_lab(lab_id: int, db: Session = Depends(get_db)):
    lab = db.query(models.Labs).filter(models.Labs.id == lab_id).first()
    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found")
    return db.query(models.Instrument).filter(models.Instrument.lab_id == lab_id).all()
