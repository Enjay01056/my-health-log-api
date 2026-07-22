from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI(
    title="MY HEALTH LOG API",
    description="건강 기록을 저장하고 분석하는 API",
    version="1.0.0",
)


records = []


class RecordIn(BaseModel):
    date: str
    weight: float
    height: float
    systolic: int
    diastolic: int
    blood_sugar: int
    steps: int = 0
    sleep_hours: float = 0.0
    memo: str = ""


@app.get("/")
def read_root():
    return {
        "message": "MY HEALTH LOG API",
        "docs": "/docs",
    }