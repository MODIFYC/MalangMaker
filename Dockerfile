FROM public.ecr.aws/lambda/python:3.10

# 람다 작업 디렉토리 명시
WORKDIR ${LAMBDA_TASK_ROOT}

# 1. 라이브러리 설치 (캐시 활용)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. 현재 폴더의 모든 내용 복사 (main.py가 이 안에 있어야 함)
COPY . .

# 3. 핸들러 실행 (main.py 내의 handler 객체 호출)
CMD [ "main.handler" ]