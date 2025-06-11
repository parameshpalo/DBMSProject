from fastapi import APIRouter, Depends, HTTPException, status , Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

import models
import schemas
from db import get_db
from oauth2 import get_current_user

router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"]
)

# --------- CREATE BOOKING (User) ---------
@router.post("/", response_model=schemas.Booking)
def create_booking(
    booking_data: schemas.BookingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Optional: prevent double booking
    overlap = db.query(models.Booking).filter(
        models.Booking.instrument_id == booking_data.instrument_id,
        models.Booking.slot == booking_data.slot
    ).first()

    if overlap:
        raise HTTPException(status_code=400, detail="This time slot is already booked.")

    new_booking = models.Booking(
        instrument_id=booking_data.instrument_id,
        slot=booking_data.slot,
        requested_to_id=booking_data.requested_to_id,
        requested_by_id=current_user.id,  # Set from auth user
        status="pending"  # Default value
    )

    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return new_booking



# --------- GET USER'S BOOKINGS ---------
@router.get("/me", response_model=List[schemas.Booking])
def get_my_bookings(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return db.query(models.Booking).filter(models.Booking.requested_by_id == current_user.id).all()


# --------- GET ALL BOOKINGS (Admin only, with pagination and filters) ---------
@router.get("/", response_model=List[schemas.Booking])
def get_all_bookings(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=100),
    user_id: int = None,
    instrument_id: int = None
):
    if current_user.privilege_level != "admin":
        raise HTTPException(status_code=403, detail="Only admins can view all bookings")

    query = db.query(models.Booking)

    if user_id:
        query = query.filter(models.Booking.requested_by_id == user_id)

    if instrument_id:
        query = query.filter(models.Booking.instrument_id == instrument_id)

    return query.offset(skip).limit(limit).all()
