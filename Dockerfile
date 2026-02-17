# 1. 베이스 이미지 설정 (소스에 명시된 Python 3.10+ 반영)
FROM python:3.10-slim

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 소스 코드 및 이미지 자산 복사
COPY . .

# 5. 환경 변수 설정 (AWS 인증 정보 등은 런타임에 주입하는 것을 권장)
# ENV AWS_ACCESS_KEY_ID=your_key
# ENV AWS_SECRET_ACCESS_KEY=your_secret

# 6. FastAPI 서버 실행 (Uvicorn 사용)
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]