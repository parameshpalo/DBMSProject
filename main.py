from fastapi import FastAPI
from routers import instruments,booking,users,approving

import models
import db
models.Base.metadata.create_all(bind=db.engine)

app=FastAPI()

app.include_router(instruments.router)
app.include_router(booking.router)
app.include_router(users.router)
app.include_router(approving.router)

@app.get('/')
def root():
  return {"message":"Hello"}