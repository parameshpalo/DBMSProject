from fastapi import APIRouter, Depends, HTTPException, status , Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List,Optional
from collections import defaultdict

import pytz
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
    # No timezone handling
    naive_slot = booking_data.slot

    overlap = db.query(models.Booking).filter(
        models.Booking.instrument_id == booking_data.instrument_id,
        models.Booking.slot == naive_slot
    ).first()

    if overlap:
        raise HTTPException(status_code=400, detail="This time slot is already booked.")

    new_booking = models.Booking(
        instrument_id=booking_data.instrument_id,
        slot=naive_slot,
        requested_to_id=booking_data.requested_to_id,
        requested_by_id=current_user.id,
        status="pending"
    )

    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return new_booking



# --------- GET USER'S BOOKINGS ---------
@router.get("/me", response_model=List[schemas.Booking])
@router.get("/me", response_model=List[schemas.Booking])
def get_my_bookings(
    lab_name: Optional[str] = Query(None, description="Filter by lab name"),
    instrument_name: Optional[str] = Query(None, description="Filter by instrument name"),
    limit: int = Query(10, ge=1, le=100, description="Limit number of results (max 100)"),
    offset: int = Query(0, ge=0, description="Number of items to skip for pagination"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Base query: bookings requested by current user
    query = db.query(models.Booking).join(models.Instrument).join(models.Labs).filter(
        models.Booking.requested_by_id == current_user.id
    )

    # Apply optional filters
    if lab_name:
        query = query.filter(models.Labs.name == lab_name)

    if instrument_name:
        query = query.filter(models.Instrument.instrument_name == instrument_name)

    # Pagination
    query = query.offset(offset).limit(limit)

    return query.all()

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


from datetime import datetime, timedelta, time
from typing import List

@router.get("/availability/{lab_name}/{instrument_name}")
def get_availability(instrument_name: str, lab_name: str, db: Session = Depends(get_db)):
    from_zone = time(10, 0)
    to_zone = time(16, 0)
    slot_duration = timedelta(hours=2)
    today = datetime.now().date()
    num_days = 5

    # Step 1: Get lab
    lab = db.query(models.Labs).filter(models.Labs.name == lab_name).first()
    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found")

    # Step 2: Get all working instruments of this name in that lab
    instruments = db.query(models.Instrument).filter(
        models.Instrument.instrument_name == instrument_name,
        models.Instrument.working == True,
        models.Instrument.lab_id == lab.id
    ).all()

    if not instruments:
        raise HTTPException(status_code=404, detail="No working instruments found")

    instrument_ids = [instr.instrument_id for instr in instruments]
    total = len(instrument_ids)

    # Step 3: Get all bookings for these instruments in next 5 days
    start_datetime = datetime.combine(today, from_zone)
    end_datetime = datetime.combine(today + timedelta(days=num_days), time(23, 59))

    bookings = db.query(models.Booking).filter(
        models.Booking.instrument_id.in_(instrument_ids),
        models.Booking.slot >= start_datetime,
        models.Booking.slot <= end_datetime,
        models.Booking.status.in_([
            models.BookingStatusEnum.approved,
            models.BookingStatusEnum.pending
        ])
    ).all()

    # Helper to normalize bookings into proper slot start time
    def normalize_slot(slot_datetime):
        base_time = datetime.combine(slot_datetime.date(), time(10, 0))
        diff = slot_datetime - base_time
        if diff.total_seconds() < 0:
            return None  # Before working hours
        slot_index = int(diff.total_seconds() // (2 * 3600))  # 2-hour slots
        if slot_index >= 4:
            return None  # After working hours
        return base_time + timedelta(hours=2 * slot_index)

    # Step 4: Group bookings by normalized slot time
    bookings_by_slot = defaultdict(set)
    for b in bookings:
        normalized_slot = normalize_slot(b.slot)
        if normalized_slot is not None:
            bookings_by_slot[normalized_slot].add(b.instrument_id)

    # Step 5: Construct slot-wise availability
    result = []
    for day_offset in range(num_days):
        date = today + timedelta(days=day_offset)
        for i in range(4):  # 4 slots: 10–12, 12–2, 2–4, 4–6
            slot_start = datetime.combine(date, time(10)) + i * slot_duration
            booked = len(bookings_by_slot.get(slot_start, set()))
            available = total - booked

            result.append({
                "date": date.strftime("%A, %d %B %Y"),
                "slot": slot_start.isoformat(),
                "available": available,
                "status": f"{available} out of {total}",
                "can_book": available > 0
            })

    return result