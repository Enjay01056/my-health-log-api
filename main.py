import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI(
    title="MY HEALTH LOG API",
    description="건강 기록을 저장하고 분석하는 API",
    version="1.0.0",
)


# 건강 기록을 저장할 JSON 파일의 위치를 지정한다.
DATA_FILE = Path(__file__).resolve().parent / "data.json"


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


# JSON 파일에서 건강 기록을 불러온다.
def load_records() -> list[dict]:
    # 저장 파일이 아직 없으면 빈 리스트를 반환한다.
    if not DATA_FILE.exists():
        return []

    try:
        # UTF-8 형식으로 JSON 파일을 읽는다.
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        # 파일 내용이 리스트인 경우에만 건강 기록으로 사용한다.
        if isinstance(data, list):
            return data

        # 리스트가 아닌 데이터가 저장되어 있으면 빈 리스트를 반환한다.
        return []

    # JSON 형식이 잘못되었거나 파일을 읽지 못한 경우 빈 리스트를 반환한다.
    except (json.JSONDecodeError, OSError):
        return []


# 건강 기록을 JSON 파일에 저장한다.
def save_records(records_data: list[dict]) -> None:
    try:
        # 한글이 깨지지 않도록 UTF-8 형식으로 저장한다.
        with DATA_FILE.open("w", encoding="utf-8") as file:
            json.dump(
                records_data,
                file,
                ensure_ascii=False,
                indent=2,
            )

    # 파일 저장에 실패하면 서버가 종료되지 않고 오류 응답을 반환하도록 한다.
    except OSError as error:
        raise HTTPException(
            status_code=500,
            detail="건강 기록을 저장하는 중 오류가 발생했습니다.",
        ) from error


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


# 서버가 시작될 때 JSON 파일에 저장된 건강 기록을 불러온다.
records = load_records()


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

    # 변경된 건강 기록을 JSON 파일에 저장한다.
    save_records(records)

    # 저장된 건강 기록을 반환한다.
    return record_data


# 전체 건강 기록 조회
@app.get("/records")
def get_records():
    return {
        "count": len(records),
        "records": records,
    }


# 시작일과 종료일 사이의 건강 기록을 검색한다.
@app.get("/search")
def search_records(start: str, end: str):
    # 시작일이 종료일보다 늦으면 400 오류를 반환한다.
    if start > end:
        raise HTTPException(
            status_code=400,
            detail="시작일은 종료일보다 늦을 수 없습니다.",
        )

    # 시작일과 종료일을 모두 포함하여 기록을 검색한다.
    search_results = [
        record
        for record in records
        if start <= record["date"] <= end
    ]

    # 검색 조건과 검색 결과를 반환한다.
    return {
        "start": start,
        "end": end,
        "count": len(search_results),
        "records": search_results,
    }


# 저장된 건강 기록의 평균 통계를 계산한다.
@app.get("/stats")
def get_stats():
    # 저장된 기록이 없으면 계산할 수 있는 통계가 없음을 반환한다.
    if not records:
        return {
            "count": 0,
            "average_weight": None,
            "average_bmi": None,
            "average_systolic": None,
            "average_diastolic": None,
            "average_blood_sugar": None,
            "average_steps": None,
            "average_sleep_hours": None,
        }

    # 저장된 건강 기록의 개수를 구한다.
    record_count = len(records)

    # 각 건강 항목의 평균을 계산한다.
    average_weight = sum(
        record["weight"] for record in records
    ) / record_count

    average_bmi = sum(
        record["bmi"] for record in records
    ) / record_count

    average_systolic = sum(
        record["systolic"] for record in records
    ) / record_count

    average_diastolic = sum(
        record["diastolic"] for record in records
    ) / record_count

    average_blood_sugar = sum(
        record["blood_sugar"] for record in records
    ) / record_count

    average_steps = sum(
        record["steps"] for record in records
    ) / record_count

    average_sleep_hours = sum(
        record["sleep_hours"] for record in records
    ) / record_count

    # 평균 결과를 소수점 둘째 자리까지 반올림하여 반환한다.
    return {
        "count": record_count,
        "average_weight": round(average_weight, 2),
        "average_bmi": round(average_bmi, 2),
        "average_systolic": round(average_systolic, 2),
        "average_diastolic": round(average_diastolic, 2),
        "average_blood_sugar": round(average_blood_sugar, 2),
        "average_steps": round(average_steps, 2),
        "average_sleep_hours": round(average_sleep_hours, 2),
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

            # 변경된 건강 기록을 JSON 파일에 저장한다.
            save_records(records)

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

            # 변경된 건강 기록을 JSON 파일에 저장한다.
            save_records(records)

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