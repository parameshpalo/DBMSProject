from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext

import models, schemas, oauth2
from db import get_db

router = APIRouter(
    prefix="/user",
    tags=["User"]
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ----------- SIGNUP -----------
@router.post("/signup", response_model=schemas.User)
def signup(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed_password = pwd_context.hash(user_data.password)

    new_user = models.User(
        username=user_data.username,
        password=hashed_password,
        privilege_level=user_data.privilege_level
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# ----------- LOGIN -----------
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()

    if not user or not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(status_code=403, detail="Invalid Credentials")

    access_token = oauth2.create_access_token(data={"user_id": user.id})

    return {"access_token": access_token, "token_type": "bearer"}
