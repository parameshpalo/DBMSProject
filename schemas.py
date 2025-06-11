from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum as PyEnum


# ----------- ENUMS -----------
class PrivilegeLevel(str, PyEnum):
    user = "user"
    admin = "admin"

class BookingStatus(str, PyEnum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

# ----------- LABS -----------
class LabBase(BaseModel):
    name: str

class LabCreate(LabBase):
    pass

class Lab(LabBase):
    id: int
    class Config:
        orm_mode = True


# ----------- INSTRUMENT SCHEMAS -----------
class InstrumentBase(BaseModel):
    instrument_name: str
    lab_id: int
    working: Optional[bool] = True

class InstrumentCreate(InstrumentBase):
    pass

class Instrument(InstrumentBase):
    instrument_id: int

    class Config:
        orm_mode = True


# ----------- USER SCHEMAS -----------
class UserBase(BaseModel):
    username: str
    privilege_level: PrivilegeLevel

class UserCreate(UserBase):
    password: str
    pass

class User(UserBase):
    id: int

    class Config:
        orm_mode = True


# ----------- BOOKING SCHEMAS -----------

class BookingBase(BaseModel):
    instrument_id: int
    slot: datetime
    requested_by_id: int
    requested_to_id: int
    status: Optional[BookingStatus] = BookingStatus.pending

class BookingCreate(BookingBase):
    pass

class Booking(BookingBase):
    id: int

    class Config:
        orm_mode = True

# ----------- BOOKING UPDATE SCHEMA -----------
class BookingStatusUpdate(BaseModel):
    status: BookingStatus

