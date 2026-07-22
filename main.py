from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI(
    title="MY HEALTH LOG API",
    description="건강 기록을 저장하고 분석하는 API",
    version="1.0.0",
)


# 건강 기록을 임시로 저장하는 리스트
# 현재는 서버를 종료하면 저장된 기록이 사라진다.
records = []


# 사용자가 입력할 건강 기록의 형식
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

# 몸무게(kg)와 키(cm)를 사용하여 BMI를 계산한다.
def calculate_bmi(weight: float, height: float) -> float:
    height_m = height / 100
    bmi = weight / (height_m ** 2)

    return round(bmi, 2)

# Classify BMI value
def classify_bmi(bmi: float) -> str:
    if bmi < 18.5:
        return "저체중"
    elif bmi < 23:
        return "정상"
    elif bmi < 25:
        return "과체중"
    else:
        return "비만"

 # Classify blood pressure
def classify_blood_pressure(
    systolic: int,
    diastolic: int,
) -> str:
    if systolic >= 140 or diastolic >= 90:
        return "고혈압"
    elif systolic >= 120 or diastolic >= 80:
        return "주의"
    else:
        return "정상"

# Classify fasting blood sugar
def classify_blood_sugar(blood_sugar: int) -> str:
    if blood_sugar < 100:
        return "정상"
    elif blood_sugar < 126:
        return "공복혈당장애"
    else:
        return "당뇨 의심"

# 기본 주소
@app.get("/")
def read_root():
    return {
        "message": "MY HEALTH LOG API에 오신 것을 환영합니다.",
        "docs": "/docs",
    }


# 건강 기록 추가
@app.post("/records")
def create_record(record: RecordIn):
    # 저장된 기록이 있으면 가장 큰 ID에 1을 더한다.
    if records:
        new_id = max(item["id"] for item in records) + 1
    else:
        new_id = 1

    # Pydantic 모델을 딕셔너리로 변환한다.
    record_data = record.model_dump()

    # BMI를 계산하고 분류한다.
    bmi = calculate_bmi(
        weight=record.weight,
        height=record.height,
    )
    bmi_category = classify_bmi(bmi)

    bp_category = classify_blood_pressure(
        systolic=record.systolic,
        diastolic=record.diastolic,
    )

    sugar_category = classify_blood_sugar(
        blood_sugar=record.blood_sugar,
    )

    # ID와 BMI 분석 결과를 기록에 추가한다.
    record_data["id"] = new_id
    record_data["bmi"] = bmi
    record_data["bmi_category"] = bmi_category
    record_data["bp_category"] = bp_category
    record_data["sugar_category"] = sugar_category
    
    # records 리스트에 저장한다.
    records.append(record_data)

    # 저장된 기록을 반환한다.
    return record_data

# 전체 건강 기록 조회
@app.get("/records")
def get_records():
    return {
        "count": len(records),
        "records": records,
    }


# 특정 건강 기록 조회
@app.get("/records/{record_id}")
def get_record(record_id: int):
    # 저장된 기록을 하나씩 확인한다.
    for record in records:
        if record["id"] == record_id:
            return record

    # 같은 ID의 기록이 없으면 404 오류를 반환한다.
    raise HTTPException(
        status_code=404,
        detail="건강 기록을 찾을 수 없습니다.",
    )

@app.delete("/records/{record_id}")
def delete_record(record_id: int):
    for index, record in enumerate(records):
        if record["id"] == record_id:
            deleted_record = records.pop(index)

            return {
                "message": "건강 기록이 삭제되었습니다.",
                "deleted_id": deleted_record["id"],
            }

    raise HTTPException(
        status_code=404,
        detail="건강 기록을 찾을 수 없습니다.",
    )