# Python 3.13 경량 이미지를 사용한다.
FROM python:3.13-slim

# 컨테이너 내부 작업 폴더를 지정한다.
WORKDIR /app

# 필요한 라이브러리 목록을 먼저 복사한다.
COPY requirements.txt .

# FastAPI와 Uvicorn을 설치한다.
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 파일을 복사한다.
COPY main.py .

# FastAPI 서버가 사용할 포트를 표시한다.
EXPOSE 8000

# 외부에서 접근할 수 있도록 서버를 실행한다.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]