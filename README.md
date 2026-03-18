# 🍡 말랑이 메이커 (Malang Maker)

> **AWS 서버리스 기반의 카카오톡 챗봇 육성 시뮬레이션 게임**  
> 사용자가 카카오톡을 통해 자신만의 캐릭터 '말랑이'를 육성하는 게임형 챗봇입니다.  
> 비정형 트래픽에 최적화된 서버리스 아키텍처와 실시간 데이터 정합성, 전광판 스타일 UX가 특징입니다.

<br>

## 🎮 주요 기능 및 UI

<table>
  <tr align="center">
    <th>🧶 말랑이 밥주기</th>
    <th>🏆 실시간 랭킹 시스템</th>
    <th>📜 명령어 가이드 (UX)</th>
  </tr>
  <tr align="center">
    <td>
      <img src="https://github.com/user-attachments/assets/d43f528c-89a1-4234-a4e8-084dfe48fd47" width="250">
    </td>
    <td>
      <img src="https://github.com/user-attachments/assets/0b461d9a-cd00-4a67-9aec-153398dae973" width="250">
    </td>
    <td>
      <img src="https://github.com/user-attachments/assets/1cd8cfec-beea-498c-8be2-39d7597f7eb8" width="250">
    </td>
  </tr>
</table>

---

## 🏗️ 아키텍처 다이어그램

![말랑이 AWS Architecture](https://github.com/user-attachments/assets/e8e6ce69-c7cf-4a95-bff4-073b2dfc2ac7)

---

## 🛠️ 기술 스택

| 분류 | 기술 |
|------|------|
| **Interface** | Kakao i OpenBuilder (Skill Server) |
| **Backend** | FastAPI (Python 3.10+) |
| **Database** | AWS DynamoDB |
| **Compute** | AWS Lambda (서버리스) |
| **API** | AWS API Gateway |
| **Container** | Docker, AWS ECR |
| **IaC** | AWS SAM, Terraform |
| **CI/CD** | GitHub Actions |
| **Monitoring** | AWS CloudWatch, AWS Budgets, SNS |
| **Notification** | Slack (Webhook) |

---

## ☁️ AWS 인프라 설계 이유

### Lambda + API Gateway (서버리스 선택)
카카오톡 챗봇 특성상 트래픽이 불규칙적으로 발생합니다. EC2처럼 서버를 상시 운영하면 유휴 시간에도 비용이 발생하지만, Lambda는 **요청이 있을 때만 실행**되어 비용 효율적입니다. 또한 트래픽 급증 시 자동으로 스케일링되어 별도 대응이 불필요합니다.

### DynamoDB (NoSQL 선택)
말랑이의 캐릭터 데이터는 레벨, 스탯, 아이템 등 구조가 유연하게 변화합니다. RDS 같은 관계형 DB는 스키마 변경 시 마이그레이션이 필요하지만, DynamoDB는 **스키마 유연성**을 제공합니다. 또한 서버리스 환경에서 RDS의 VPC 연결 없이 간단히 연동할 수 있습니다.

### ECR (컨테이너 이미지 관리)
Lambda를 컨테이너 이미지 방식으로 배포하여 의존성 충돌 없이 일관된 실행 환경을 보장합니다. ECR은 AWS 내부 네트워크로 Lambda와 연결되어 이미지 Pull 속도가 빠릅니다.

---

## 🔄 CI/CD 파이프라인

main 브랜치에 Push 시 GitHub Actions가 자동으로 빌드 및 배포를 수행합니다.

```
GitHub Push (main)
    ↓
GitHub Actions (deploy.yaml)
    ↓
SAM Build --use-container   # Docker 이미지 빌드
    ↓
ECR Push                    # 이미지 저장
    ↓
SAM Deploy                  # CloudFormation 스택 업데이트
    ↓
Lambda 자동 업데이트 완료
```

Terraform 변경 시에는 `terraform.yaml` 워크플로우가 실행됩니다.

```
my_terraform/ 변경 감지
    ↓
terraform init (S3 Remote Backend)
    ↓
PR: terraform plan   # 변경 사항 미리 확인
    ↓
main 머지: terraform apply   # 실제 적용
```

---

## 🔐 IAM 최소권한 전략

운영 목적에 따라 IAM 그룹을 분리하여 최소권한원칙(Least Privilege)을 적용했습니다.

| 그룹 | 용도 | 주요 권한 |
|------|------|-----------|
| `malang-dev` | 일반 개발 | IAMReadOnly + 서비스 권한 |
| `malang-ops` | 운영/모니터링 | SNS + CloudWatch + Budgets |
| `malang-deployer` | CI/CD 전용 | IAMFullAccess + 배포 권한 |

**핵심 원칙:**
- 평상시 `IAMReadOnlyAccess` 유지 → SAM 배포 시에만 `malang-deployer` 사용
- GitHub Actions에는 배포 전용 키(`malang-deployer`)만 등록
- 모든 IAM 리소스는 **Terraform으로 코드화**하여 S3 Remote Backend로 상태 관리

---

## 📊 모니터링 구성

CloudWatch + SNS + Slack 파이프라인으로 운영 이슈를 실시간으로 감지합니다.

| 알람 | 조건 |
|------|------|
| Lambda Errors | 에러 1회 이상 발생 시 |
| API Gateway 5XXError | 서버 에러 1회 이상 발생 시 |
| DynamoDB ConsumedWriteCapacity | 쓰기 용량 임계치 초과 시 |
| AWS Budgets | 월 $1 예산의 80% 초과 시 |

알람 발생 → SNS → Lambda(`malang-slack-alarm`) → Slack Webhook → 실시간 알림 수신

---

## 📂 프로젝트 구조

```
MalangMaker/
├── main.py                  # FastAPI 서버 및 카카오톡 스킬 엔드포인트
├── database.py              # DynamoDB CRUD 및 게임 엔진 핵심 로직
├── descriptions.py          # 말랑이 타입별 대사 및 진화 데이터
├── images/                  # 레벨별 말랑이 이미지 자산
├── Dockerfile               # 컨테이너 빌드 설정
├── template.yaml            # SAM 배포 설정
├── samconfig.toml           # SAM 배포 파라미터
├── my_terraform/            # Terraform IaC (IAM 리소스)
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── .github/workflows/
│   ├── deploy.yaml          # SAM 자동 배포
│   └── terraform.yaml       # Terraform 자동 적용
└── README.md
```

---

## 🔥 트러블슈팅

<details>
<summary><b>이슈 1: 카카오톡 NetworkAccessForbidden — 응답 자체가 없음</b></summary>

- **현상**: 카카오톡 채널에서 메시지를 보내도 응답이 없고, 카카오 설정 페이지에서 '네트워크 오류'만 표시. 503 같은 에러 코드조차 뜨지 않음.
- **원인**: Dockerfile의 베이스 이미지 문제. 일반 `python:3.10-slim` 이미지를 사용했는데, AWS Lambda는 전용 런타임 환경이 필요함. 일반 이미지를 쓰면 Lambda가 Init 단계조차 실패하여 카카오 입장에서는 연결 거부로 판단.
- **해결**: 베이스 이미지를 AWS 공식 Lambda 전용 이미지로 변경.

```dockerfile
# 변경 전
FROM python:3.10-slim

# 변경 후
FROM public.ecr.aws/lambda/python:3.10
```
</details>

<details>
<summary><b>이슈 2: 카카오톡 NetworkAccessForbidden — 503 에러</b></summary>

- **현상**: 카카오 챗봇에서 응답이 없고 네트워크 오류 발생.
- **원인**: Lambda 내부에서 500대 에러가 발생하면 카카오 측에서 연결을 강제로 끊음.
- **접근**: `sam logs -n MalangMakerFunction --stack-name malang-maker --tail` 로 Lambda 로그 직접 확인.
- **해결**: Mangum lifespan 옵션 수정 후 재배포.

```python
# 변경 전
handler = Mangum(app)

# 변경 후
handler = Mangum(app, lifespan="off")
```
</details>

<details>
<summary><b>이슈 3: Runtime.ImportModuleError — Unable to import module 'main'</b></summary>

- **현상**: Lambda 로그에서 `main.py`를 찾지 못하는 에러 발생.
- **원인**: 이미지 경로가 꼬이거나 기존 빌드 캐시가 엉뚱하게 올라간 상태.
- **해결**: 빌드 캐시 완전 삭제 후 재빌드.

```bash
rmdir /s /q .aws-sam           # 캐시 완전 삭제
sam build --use-container      # Docker 환경에서 재빌드
sam deploy                     # 재배포
```
</details>

<details>
<summary><b>이슈 4: AWS_REGION 예약어 충돌</b></summary>

- **현상**: `template.yaml` 환경 변수에 `AWS_REGION`을 설정하자 배포 경고 발생, Lambda 실행 시 리전 정보를 제대로 못 불러옴.
- **원인**: `AWS_REGION`은 Lambda 런타임이 자동으로 설정하는 예약 환경 변수. 사용자가 임의로 덮어쓰려 하면 충돌 경고가 발생하거나 값이 무시됨.
- **해결**: 커스텀 변수명으로 변경.

```yaml
# 변경 전
Variables:
  AWS_REGION: ap-northeast-2   # 예약어 — 위험!

# 변경 후
Variables:
  MY_APP_REGION: ap-northeast-2  # 안전한 커스텀 변수
```
</details>

<details>
<summary><b>이슈 5: 이미지 파일 증발 — .dockerignore 실수</b></summary>

- **현상**: 배포 후 Lambda 로그에서 이미지 파일을 찾지 못하는 에러 발생.
- **원인**: `.dockerignore`에 `images/` 폴더가 실수로 포함되어 이미지만 컨테이너에 포함되지 않음.
- **해결**: `.dockerignore`에서 해당 줄 제거 후 재빌드 및 재배포.
</details>

<details>
<summary><b>이슈 6: {"detail":"Method Not Allowed"} — 사실 성공의 증거</b></summary>

- **현상**: 배포 성공 후 API Gateway URL로 브라우저 접속 시 `{"detail":"Method Not Allowed"}` 응답.
- **원인(아닌 이유)**: 브라우저 주소창은 GET 요청을 보내지만, API는 POST만 허용하도록 설계됨. FastAPI가 정상적으로 방어한 것.
- **결론**: 에러가 아니라 서버가 정상 동작하고 있다는 신호. ✅
</details>

<details>
<summary><b>이슈 7: Terraform Remote Backend — EntityAlreadyExists 충돌</b></summary>

- **현상**: GitHub Actions에서 `terraform apply` 실행 시 IAM 유저/그룹 전부 `EntityAlreadyExists` 에러.
- **원인**: 로컬에서 `terraform import`로 가져온 `terraform.tfstate`가 `.gitignore`에 의해 GitHub에 올라가지 않음. GitHub Actions는 빈 state에서 시작하여 기존 리소스를 새로 만들려다 충돌.
- **해결**: S3 Remote Backend 설정으로 state 파일을 중앙 관리.

```hcl
backend "s3" {
  bucket = "aws-sam-cli-managed-default-samclisourcebucket-xxxx"
  key    = "iam/terraform.tfstate"
  region = "ap-northeast-2"
}
```

```bash
terraform init -migrate-state  # 로컬 state → S3 마이그레이션
```
</details>

---

## 🔗 서비스 링크

카카오톡에서 **말랑이 메이커** 채널을 추가하고 직접 육성해보세요!

👉 [말랑이 메이커 카카오톡 채널](https://pf.kakao.com/_kRFRX)

---

## 👤 Author

- **이름**: 최수정
- **Blog**: [https://cmod-ify.tistory.com/](https://cmod-ify.tistory.com/)
- **Keywords**: AWS Solutions Architect, Backend Developer, Python Enthusiast