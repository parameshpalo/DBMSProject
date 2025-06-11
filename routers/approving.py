from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

import models, schemas
from db import get_db
from oauth2 import get_current_user

router = APIRouter(
    prefix="/approving",
    tags=["Approving"]
)

# --------- GET BOOKINGS TO APPROVE (for profs/admins) ---------
@router.get("/to_approve", response_model=List[schemas.Booking])
def get_bookings_to_approve(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return db.query(models.Booking).filter(
        models.Booking.requested_to_id == current_user.id
    ).all()


# --------- APPROVE OR REJECT BOOKING ---------
@router.put("/{booking_id}/decision", response_model=schemas.Booking)
def approve_or_reject_booking(
    booking_id: int,
    decision: schemas.BookingStatusUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.requested_to_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to make a decision on this booking")

    booking.status = decision.status
    db.commit()
    db.refresh(booking)
    return booking
