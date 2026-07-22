# my-health-log-api
FastAPI와 Docker를 활용한 개인 건강 기록 관리 API

매일 측정한 체중, 키, 혈압, 공복 혈당 등의 건강 기록을 저장하고 관리하는 REST API입니다.

입력된 건강 정보를 바탕으로 BMI를 계산하고, BMI·혈압·혈당 상태와 건강 경고를 자동으로 제공합니다.

> 이 프로젝트의 건강 분류 결과는 과제에서 제시된 기준을 사용하며, 실제 의료 진단을 대신하지 않습니다.

---

## 프로젝트 목표

- 개인 건강 기록 추가, 조회, 수정, 삭제
- BMI 자동 계산
- BMI 상태 분류
- 혈압 상태 분류
- 공복 혈당 상태 분류
- 위험 상태 경고 제공
- 날짜 범위 검색
- 건강 기록 통계 제공
- JSON 파일을 이용한 데이터 저장
- Docker 환경에서 실행

---

## 주요 기능

### 건강 기록 관리

- 건강 기록 추가
- 전체 건강 기록 조회
- 특정 건강 기록 조회
- 건강 기록 수정
- 건강 기록 삭제

### 건강 정보 분석

- BMI 계산 및 분류
- 혈압 상태 분류
- 공복 혈당 상태 분류
- 위험 상태에 따른 경고 메시지 생성

### 검색 및 통계

- 시작일과 종료일을 이용한 날짜 범위 검색
- 평균 체중, 평균 BMI 등의 통계 제공

---

## 건강 기록 입력 항목

| 필드 | 자료형 | 필수 여부 | 설명 |
|---|---:|---:|---|
| `date` | 문자열 | 필수 | 측정 날짜, `YYYY-MM-DD` 형식 |
| `weight` | 실수 | 필수 | 몸무게, 단위 kg |
| `height` | 실수 | 필수 | 키, 단위 cm |
| `systolic` | 정수 | 필수 | 수축기 혈압 |
| `diastolic` | 정수 | 필수 | 이완기 혈압 |
| `blood_sugar` | 정수 | 필수 | 공복 혈당, 단위 mg/dL |
| `steps` | 정수 | 선택 | 하루 걸음 수, 기본값 0 |
| `sleep_hours` | 실수 | 선택 | 수면 시간, 기본값 0 |
| `memo` | 문자열 | 선택 | 건강 기록 메모 |

---

## 건강 상태 판정 기준

### BMI

| BMI | 분류 |
|---:|---|
| 18.5 미만 | 저체중 |
| 18.5 이상 23 미만 | 정상 |
| 23 이상 25 미만 | 과체중 |
| 25 이상 | 비만 |

### 혈압

| 조건 | 분류 |
|---|---|
| 수축기 140 이상 또는 이완기 90 이상 | 고혈압 |
| 수축기 120~139 또는 이완기 80~89 | 주의 |
| 수축기 120 미만이고 이완기 80 미만 | 정상 |

혈압은 `고혈압 → 주의 → 정상` 순서로 판정합니다.

### 공복 혈당

| 공복 혈당 | 분류 |
|---:|---|
| 100 미만 | 정상 |
| 100 이상 126 미만 | 공복혈당장애 |
| 126 이상 | 당뇨 의심 |

### 경고 생성 조건

다음 조건에 해당할 때 경고 메시지를 반환합니다.

- BMI 분류가 `비만`
- 혈압 분류가 `고혈압`
- 혈당 분류가 `당뇨 의심`

위험 조건이 없으면 빈 배열을 반환합니다.

```json
{
  "warnings": []
}
```

---

## API 엔드포인트

| Method | Endpoint | 설명 | 진행 상태 |
|---|---|---|---|
| `POST` | `/records` | 건강 기록 추가 | 구현 완료 |
| `GET` | `/records` | 전체 건강 기록 조회 | 구현 완료 |
| `GET` | `/records/{record_id}` | 특정 건강 기록 조회 | 구현 완료 |
| `PUT` | `/records/{record_id}` | 특정 건강 기록 수정 | 구현 완료 |
| `DELETE` | `/records/{record_id}` | 특정 건강 기록 삭제 | 구현 완료 |
| `GET` | `/search` | 날짜 범위로 건강 기록 검색 | 구현 예정 |
| `GET` | `/stats` | 건강 기록 통계 조회 | 구현 예정 |

FastAPI 실행 후 다음 주소에서 API를 직접 테스트할 수 있습니다.

```text
http://127.0.0.1:8000/docs
```

---

## 기술 스택

- Python
- FastAPI
- Pydantic
- Uvicorn
- JSON
- Docker
- Git
- GitHub

---

## 프로젝트 구조

```text
my-health-log-api/
├── main.py
├── requirements.txt
├── Dockerfile
├── .gitignore
├── .dockerignore
├── README.md
└── data.example.json
```

실행 과정에서 생성되는 다음 파일과 폴더는 GitHub에 포함하지 않습니다.

```text
venv/
__pycache__/
data.json
```

---

## 로컬 실행 방법

### 1. 저장소 내려받기

```bash
git clone https://github.com/Enjay01056/my-health-log-api
cd my-health-log-api
```

### 2. 가상환경 생성

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Windows 명령 프롬프트:

```cmd
python -m venv venv
venv\Scripts\activate.bat
```

### 3. 패키지 설치

```bash
pip install -r requirements.txt
```

### 4. 서버 실행

```bash
uvicorn main:app --reload
```

### 5. 접속 주소

기본 주소:

```text
http://127.0.0.1:8000
```

API 문서:

```text
http://127.0.0.1:8000/docs
```

---

## Docker 실행 방법

Docker 설정 구현 후 작성할 예정입니다.

```bash
docker build -t my-health-log-api .
docker run -p 8000:8000 my-health-log-api
```

---

## 데이터 저장

건강 기록은 프로젝트의 `data.json` 파일에 저장할 예정입니다.

실제 건강 정보가 포함될 수 있으므로 `data.json`은 GitHub에 올리지 않습니다. 데이터 형식 확인을 위한 예제 파일로 `data.example.json`을 제공합니다.

---

## 프로젝트 규칙

### 현재 적용된 규칙

- 하나의 기록에는 현재 저장된 다른 기록과 겹치지 않는 ID를 부여합니다.
- 기록을 수정할 때 기존 ID는 유지합니다.
- 기록을 수정하면 BMI와 건강 분류 및 경고 결과를 다시 계산합니다.
- 존재하지 않는 기록을 조회·수정·삭제하면 `404` 오류를 반환합니다.

### 구현 예정 규칙

- 날짜 검색은 시작일과 종료일을 모두 포함합니다.
- 잘못된 입력이 들어와도 서버가 종료되지 않도록 처리합니다.
- 서버를 종료하고 다시 실행해도 건강 기록이 유지되도록 JSON 파일에 저장합니다.

---

## 개발 진행 상황

- [x] GitHub 저장소 생성
- [x] Python 프로젝트 환경 설정
- [x] FastAPI 기본 서버 설정
- [x] Pydantic 입력 모델 작성
- [x] 건강 기록 추가 API
- [x] 전체 및 단건 조회 API
- [x] 건강 기록 수정 API
- [x] 건강 기록 삭제 API
- [x] BMI 계산 및 분류
- [x] 혈압 및 혈당 분류
- [x] 건강 경고 생성
- [ ] 날짜 범위 검색
- [ ] 건강 기록 통계
- [ ] JSON 파일 저장
- [ ] Docker 설정
- [ ] 최종 테스트 및 문서 정리

---

## 배포 주소

현재 배포하지 않았습니다.