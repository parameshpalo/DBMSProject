from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from db import Base

class PrivilegeLevelEnum(str, enum.Enum):
    user = "user"
    admin = "admin"

class BookingStatusEnum(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class Labs(Base):
    __tablename__ = "labs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    instruments = relationship("Instrument", back_populates="lab")


class Instrument(Base):
    __tablename__ = "instruments"

    instrument_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    instrument_name = Column(String, nullable=False)
    lab_id = Column(Integer, ForeignKey("labs.id"), nullable=False)
    working = Column(Boolean, default=True)

    lab = relationship("Labs", back_populates="instruments")
    bookings = relationship("Booking", back_populates="instrument")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password= Column(String,nullable=False)
    privilege_level = Column(Enum(PrivilegeLevelEnum), nullable=False)

    bookings_requested = relationship("Booking", foreign_keys='Booking.requested_by_id', back_populates="requested_by")
    bookings_approved = relationship("Booking", foreign_keys='Booking.requested_to_id', back_populates="requested_to")


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    instrument_id = Column(Integer, ForeignKey("instruments.instrument_id"), nullable=False)
    slot = Column(DateTime, nullable=False)
    
    requested_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    requested_to_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    status = Column(Enum(BookingStatusEnum), default=BookingStatusEnum.pending, nullable=False)


    instrument = relationship("Instrument", back_populates="bookings")
    requested_by = relationship("User", foreign_keys=[requested_by_id], back_populates="bookings_requested")
    requested_to = relationship("User", foreign_keys=[requested_to_id], back_populates="bookings_approved")
