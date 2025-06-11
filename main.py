from fastapi import FastAPI
from routers import instruments

app=FastAPI()

app.include_router(instruments.router)

@app.get('/')
def root():
  return {"message":"Hello"}