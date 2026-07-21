from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field


# FastAPI 애플리케이션 생성
app = FastAPI(
    title="MY HEALTH LOG API",
    description="건강 기록을 저장하고 BMI, 혈압, 혈당 상태를 분석하는 API",
    version="1.0.0",
)


# Day 1에는 메모리의 리스트를 사용하고,
# Day 3에 JSON 파일 저장 방식으로 변경할 예정
records = []


# 사용자가 입력할 건강 기록의 형식
class RecordIn(BaseModel):
    date: str

    weight: float = Field(
        gt=0,
        description="몸무게(kg)",
    )

    height: float = Field(
        gt=0,
        description="키(cm)",
    )

    systolic: int = Field(
        gt=0,
        description="수축기 혈압",
    )

    diastolic: int = Field(
        gt=0,
        description="이완기 혈압",
    )

    blood_sugar: int = Field(
        gt=0,
        description="공복 혈당(mg/dL)",
    )

    steps: int = Field(
        default=0,
        ge=0,
        description="하루 걸음 수",
    )

    sleep_hours: float = Field(
        default=0.0,
        ge=0,
        le=24,
        description="수면 시간",
    )

    memo: str = Field(
        default="",
        description="메모",
    )


# 서버가 정상적으로 실행되는지 확인하는 기본 주소
@app.get("/")
def read_root():
    return {
        "message": "MY HEALTH LOG API",
        "docs": "/docs",
    }
