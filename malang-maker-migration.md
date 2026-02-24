# [Technical Review] 말랑이 메이커 #2: SAM으로 FastAPI 서버리스 마이그레이션 및 트러블슈팅

### 전체 아키텍처 흐름
* **FastAPI에 Mangum 부착**: 기존 웹 프레임워크를 Lambda가 이해할 수 있게 변환함.
* **Docker & ECR**: 코드를 컨테이너 이미지로 빌드하여 AWS ECR에 푸시함.
* **AWS Lambda**: 업로드된 이미지를 기반으로 서버리스 함수를 실행함.
* **API Gateway**: Lambda를 외부(카카오톡 챗봇 등)와 연결해 주는 관문 역할을 함.
* **IAM Role**: Lambda가 DynamoDB에 접근할 수 있도록 권한을 제한함.
* **AWS SAM**: 인프라 생성과 배포 과정을 템플릿 하나로 자동화함.
* **테스트**: 로컬 빌드 및 실제 환경 테스트를 진행함.

---

### 주요 코드 및 설정 변경 (SAM & FastAPI)
**1. SAM 템플릿 (template.yaml)**
* 소스 코드 직배포가 아니라 도커 이미지를 사용하므로 `PackageType: Image`로 명시함.

**2. 환경별 DB 분기 (db.py)**
* 로컬은 `.env`를 읽고, Lambda 환경은 부여된 IAM Role을 쓰도록 `os.getenv("AWS_LAMBDA_FUNCTION_NAME")` 기준으로 분기 처리함.

**3. 어댑터 장착 (main.py)**
* `handler = Mangum(app, lifespan="off")` 설정을 통해 FastAPI와 Lambda를 연결함.

**4. 도커 베이스 변경 (Dockerfile)**
* `public.ecr.aws/lambda/python:3.10`과 같은 AWS 전용 이미지로 베이스를 교체하고 `CMD ["main.handler"]`를 설정함.

### 트러블슈팅
**1. 카카오톡 NetworkAccessForbidden (응답 없음)**
* **원인**: 일반 Python slim 이미지를 사용해 Lambda 런타임이 초기화되지 못함.
* **해결**: 베이스 이미지를 AWS 전용 런타임 이미지(`public.ecr.aws/lambda/python:3.10`)로 변경함.

**2. 카카오톡 챗봇 503 에러**
* **원인**: 서버 내부 에러 발생 시 카카오에서 연결을 차단함.
* **해결**: `sam logs`로 로그를 분석하고, Mangum 설정에 `lifespan="off"`를 추가하여 수정함.

**3. Runtime.ImportModuleError (Unable to import module 'main')**
* **원인**: 빌드 캐시가 꼬여서 도커 내부의 `main.py`를 찾지 못함.
* **해결**: `.aws-sam` 폴더를 완전히 날려버리고 재빌드하여 해결함.

**4. AWS_REGION 예약어 충돌**
* **원인**: AWS 람다가 내부적으로 사용하는 예약어(`AWS_REGION`)를 환경 변수명으로 사용함.
* **해결**: 변수 이름을 `MY_APP_REGION`과 같은 커스텀 명칭으로 변경함.

**5. 이미지 파일 증발**
* **원인**: `.dockerignore` 파일에 `img` 폴더가 포함되어 서버에 이미지가 올라가지 않음.
* **해결**: 해당 항목을 삭제하고 재배포함.

**6. 브라우저 {"detail":"Method Not Allowed"} 메시지**
* **원인**: API는 POST 방식만 허용하는데 브라우저에서 GET 방식으로 접근함.
* **결론**: 에러가 아니라 서버가 정상적으로 작동하여 보안 방어가 이루어지고 있다는 증거임.