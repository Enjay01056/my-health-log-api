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


# 몸무게와 키를 이용해 BMI를 계산한다.
def calculate_bmi(weight: float, height: float) -> float:
    # 키를 cm 단위에서 m 단위로 변환한다.
    height_m = height / 100

    # BMI를 계산한다.
    bmi = weight / (height_m ** 2)

    # 소수점 둘째 자리까지 반올림하여 반환한다.
    return round(bmi, 2)


# BMI 값을 기준으로 상태를 분류한다.
def classify_bmi(bmi: float) -> str:
    if bmi < 18.5:
        return "저체중"
    elif bmi < 23:
        return "정상"
    elif bmi < 25:
        return "과체중"
    else:
        return "비만"


# 수축기 혈압과 이완기 혈압을 기준으로 혈압 상태를 분류한다.
def classify_blood_pressure(
    systolic: int,
    diastolic: int,
) -> str:
    # 고혈압 조건을 먼저 확인한다.
    if systolic >= 140 or diastolic >= 90:
        return "고혈압"

    # 고혈압이 아니면서 주의 범위에 해당하는지 확인한다.
    elif systolic >= 120 or diastolic >= 80:
        return "주의"

    # 두 조건에 해당하지 않으면 정상으로 분류한다.
    else:
        return "정상"


# 공복 혈당 값을 기준으로 혈당 상태를 분류한다.
def classify_blood_sugar(blood_sugar: int) -> str:
    if blood_sugar < 100:
        return "정상"
    elif blood_sugar < 126:
        return "공복혈당장애"
    else:
        return "당뇨 의심"


# 건강 상태에 따라 경고 메시지를 생성한다.
def create_warnings(
    bmi_category: str,
    bp_category: str,
    sugar_category: str,
) -> list[str]:
    # 경고 메시지를 저장할 빈 리스트를 만든다.
    warnings = []

    # BMI 분류가 비만이면 경고를 추가한다.
    if bmi_category == "비만":
        warnings.append("BMI가 비만 범위입니다.")

    # 혈압 분류가 고혈압이면 경고를 추가한다.
    if bp_category == "고혈압":
        warnings.append("혈압이 고혈압 범위입니다.")

    # 혈당 분류가 당뇨 의심이면 경고를 추가한다.
    if sugar_category == "당뇨 의심":
        warnings.append("공복 혈당이 당뇨 의심 범위입니다.")

    # 생성된 경고 목록을 반환한다.
    return warnings


# 입력된 건강 기록과 분석 결과를 하나의 딕셔너리로 만든다.
def build_record_data(record: RecordIn, record_id: int) -> dict:
    # Pydantic 모델을 딕셔너리로 변환한다.
    record_data = record.model_dump()

    # 키와 몸무게를 이용해 BMI를 계산한다.
    bmi = calculate_bmi(
        weight=record.weight,
        height=record.height,
    )

    # 계산된 BMI 값을 기준으로 상태를 분류한다.
    bmi_category = classify_bmi(bmi)

    # 수축기 혈압과 이완기 혈압을 기준으로 상태를 분류한다.
    bp_category = classify_blood_pressure(
        systolic=record.systolic,
        diastolic=record.diastolic,
    )

    # 공복 혈당 값을 기준으로 상태를 분류한다.
    sugar_category = classify_blood_sugar(
        blood_sugar=record.blood_sugar,
    )

    # 건강 상태에 따라 경고 메시지를 생성한다.
    warnings = create_warnings(
        bmi_category=bmi_category,
        bp_category=bp_category,
        sugar_category=sugar_category,
    )

    # 기록의 ID와 건강 분석 결과를 추가한다.
    record_data["id"] = record_id
    record_data["bmi"] = bmi
    record_data["bmi_category"] = bmi_category
    record_data["bp_category"] = bp_category
    record_data["sugar_category"] = sugar_category
    record_data["warnings"] = warnings

    # 완성된 건강 기록을 반환한다.
    return record_data


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

    # 입력 데이터와 건강 분석 결과를 하나의 기록으로 만든다.
    record_data = build_record_data(
        record=record,
        record_id=new_id,
    )

    # 완성된 기록을 리스트에 저장한다.
    records.append(record_data)

    # 저장된 건강 기록을 반환한다.
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
        # 요청한 ID와 같은 기록을 찾으면 반환한다.
        if record["id"] == record_id:
            return record

    # 같은 ID의 기록이 없으면 404 오류를 반환한다.
    raise HTTPException(
        status_code=404,
        detail="건강 기록을 찾을 수 없습니다.",
    )


# 특정 건강 기록 수정
@app.put("/records/{record_id}")
def update_record(record_id: int, record: RecordIn):
    # 저장된 기록을 순서대로 확인한다.
    for index, existing_record in enumerate(records):
        # 요청한 ID와 같은 기록을 찾는다.
        if existing_record["id"] == record_id:
            # 기존 ID는 유지하고 건강 분석 결과를 다시 계산한다.
            updated_record = build_record_data(
                record=record,
                record_id=record_id,
            )

            # 기존 기록을 수정된 기록으로 교체한다.
            records[index] = updated_record

            # 수정된 건강 기록을 반환한다.
            return updated_record

    # 같은 ID의 기록이 없으면 404 오류를 반환한다.
    raise HTTPException(
        status_code=404,
        detail="건강 기록을 찾을 수 없습니다.",
    )


# 특정 건강 기록 삭제
@app.delete("/records/{record_id}")
def delete_record(record_id: int):
    # 저장된 기록을 순서대로 확인한다.
    for index, record in enumerate(records):
        # 요청한 ID와 같은 기록을 찾는다.
        if record["id"] == record_id:
            # 해당 위치의 기록을 리스트에서 삭제한다.
            deleted_record = records.pop(index)

            # 삭제 완료 메시지와 삭제한 ID를 반환한다.
            return {
                "message": "건강 기록이 삭제되었습니다.",
                "deleted_id": deleted_record["id"],
            }

    # 같은 ID의 기록이 없으면 404 오류를 반환한다.
    raise HTTPException(
        status_code=404,
        detail="건강 기록을 찾을 수 없습니다.",
    )