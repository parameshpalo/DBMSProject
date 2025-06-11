from fastapi import FastAPI
from routers import instruments,booking,users

app=FastAPI()

app.include_router(instruments.router)
app.include_router(booking.router)
app.include_router(users.router)

@app.get('/')
def root():
  return {"message":"Hello"}