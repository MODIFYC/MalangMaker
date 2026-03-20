# 🍡 말랑이 메이커 (Malang Maker)

> **AWS 서버리스 기반의 카카오톡 챗봇 육성 시뮬레이션 게임**  
> 카카오톡을 통해 자신만의 캐릭터 '말랑이'를 육성하는 게임형 챗봇입니다.  
> 비정형 트래픽에 최적화된 서버리스 아키텍처로 설계하여 **실제 운영 중인 서비스**입니다.

👉 **[말랑이 메이커 카카오톡 채널](https://pf.kakao.com/_kRFRX)**

<br>

## 🎮 주요 기능 및 UI

<table>
  <tr align="center">
    <th>🧶 말랑이 밥주기</th>
    <th>🏆 실시간 랭킹 시스템</th>
    <th>📜 명령어 가이드 (UX)</th>
  </tr>
  <tr align="center">
    <td><img src="https://github.com/user-attachments/assets/d43f528c-89a1-4234-a4e8-084dfe48fd47" width="250"></td>
    <td><img src="https://github.com/user-attachments/assets/0b461d9a-cd00-4a67-9aec-153398dae973" width="250"></td>
    <td><img src="https://github.com/user-attachments/assets/1cd8cfec-beea-498c-8be2-39d7597f7eb8" width="250"></td>
  </tr>
</table>

---

## 🏗️ 아키텍처 다이어그램

![말랑이 AWS Architecture](https://github.com/user-attachments/assets/1f8f77e5-e1cd-4dc1-9335-af7e2e61b3c8)

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

## 🚀 성능 및 운영 성과

| 항목 | 결과 |
|------|------|
| 평균 응답시간 | 49ms |
| p95 응답시간 | 67ms |
| 에러율 | 0% |
| 콜드 스타트 | 해결 (EventBridge 웜업 적용, 최대 284ms) |
| 월 운영 비용 | $1 미만 |
| 운영 기간 | 2024.02 ~ 현재 |

> k6 부하 테스트 기준 (동시 사용자 10명, 총 1,289건 요청)  
> 서버리스 아키텍처 기반 자동 스케일링으로 트래픽 증가 대응  
> CloudWatch + SNS + Slack 기반 실시간 모니터링 운영 중

---

## ☁️ AWS 인프라 설계 이유

### Lambda + API Gateway
카카오톡 챗봇 특성상 트래픽이 불규칙적으로 발생합니다. Lambda는 **요청 시에만 실행**되어 유휴 비용이 없고, 트래픽 급증 시 자동 스케일링됩니다. → **월 비용 $1 미만 달성**

### DynamoDB (NoSQL)
캐릭터 데이터 스키마가 레벨/진화 단계마다 유연하게 변화합니다. RDS 대비 스키마 변경 시 마이그레이션이 불필요하고, VPC 없이 Lambda와 직접 연동됩니다.

### ECR + Container Image
Lambda를 컨테이너 이미지 방식으로 배포하여 의존성 충돌 없는 일관된 실행 환경을 보장합니다.

---

## 🔐 IAM 최소권한 전략

운영 목적에 따라 IAM 그룹을 분리하여 최소권한원칙(Least Privilege)을 적용했습니다.

| 그룹 | 용도 | 주요 권한 |
|------|------|-----------|
| `malang-dev` | 일반 개발 | IAMReadOnly + 서비스 권한 |
| `malang-ops` | 운영/모니터링 | SNS + CloudWatch + Budgets |
| `malang-deployer` | CI/CD 전용 | IAMFullAccess + 배포 권한 |

- 평상시 `IAMReadOnlyAccess` 유지 → SAM 배포 시에만 `malang-deployer` 사용
- 모든 IAM 리소스는 **Terraform으로 코드화** + S3 Remote Backend로 상태 관리

---

## 🔄 CI/CD 파이프라인

```
GitHub Push (main)
    ↓
GitHub Actions (deploy.yaml)
    ↓
SAM Build --use-container → ECR Push → SAM Deploy
    ↓
Lambda 자동 업데이트 완료
```

Terraform 변경 시 `terraform.yaml` 워크플로우가 실행됩니다.

```
my_terraform/ 변경 감지 → terraform init (S3 Backend)
    ↓
PR: terraform plan  →  main 머지: terraform apply
```

---

## 📊 모니터링 구성

| 알람 | 조건 |
|------|------|
| Lambda Errors | 에러 1회 이상 발생 시 |
| API Gateway 5XXError | 서버 에러 1회 이상 발생 시 |
| DynamoDB ConsumedWriteCapacity | 쓰기 용량 임계치 초과 시 |
| AWS Budgets | 월 $1 예산의 80% 초과 시 |

알람 발생 → SNS → Lambda(`malang-slack-alarm`) → Slack Webhook → 실시간 알림 수신

---

### 테스트 시나리오
| 단계 | 내용 | 목적 |
|------|------|------|
| 1단계 | 평상시 트래픽 (2명) | 기준값 측정 |
| 2단계 | 50명 동시 폭증 | 자동 스케일링 검증 |
| 3단계 | 15분 유휴 대기 | Lambda 컨테이너 종료 확인 |
| 4단계 | 콜드 스타트 후 재폭증 | 콜드 스타트 + 동시 요청 조합 |
| 5단계 | 10분 지속 부하 | 안정성 검증 |
| 6단계 | 쓰다듬기/똥치우기 집중 테스트 | 하루 1회 제한 로직 + DB 쓰기 검증 |

총 테스트 시간: 약 33분 / 동시 사용자 최대 50명

### 1차 테스트 결과 (종합 시나리오)

| 지표 | 결과 |
|------|------|
| 평균 응답시간 | 45ms |
| p95 응답시간 | 63.84ms |
| 최대 응답시간 | 1.52s (콜드 스타트) |
| 에러율 | 6.62% → 버그 발견 |
| Throttle | 미발생 |
| Lambda Errors | 0건 |

### 버그 발견 및 수정
- **발견**: 에러율 6.62% 초과 → CloudWatch Logs 필터링으로 `KeyError: 'none'` 확인
- **원인**: 사망 상태(`health: 0`) 말랑이의 `type`이 `"none"`으로 저장된 유저에 대해 쓰다듬기 예외처리 누락
- **수정**: 사망 상태 체크 로직 추가

### 2차 테스트 결과 (버그 수정 후 — 쓰다듬기/똥치우기 집중)

| 지표 | 쓰다듬기 | 똥치우기 |
|------|---------|---------|
| 평균 응답시간 | 50ms | 56ms |
| p95 응답시간 | 70ms | 75ms |
| 최대 응답시간 |     6s (콜드 스타트) |
| 에러율 | 0%  | 0%  |
| Throttle | 미발생 | 미발생 |

### 분석
- **콜드 스타트**: 15분 유휴 후 첫 요청 최대 6s → 이후 16ms로 안정화 (서버리스 특성)
- **자동 스케일링**: 50명 동시 요청에서 Throttle 0건 → Lambda 자동 확장 정상 동작
- **비즈니스 로직 안정성**: 하루 1회 제한, DB 쓰기 로직 동시 요청에서도 정상 동작 확인

### 3차 테스트 결과 (웜업 적용 후 — 콜드 스타트 개선 확인)

| 지표 | 결과 |
|------|------|
| 평균 응답시간 | 56ms |
| p95 응답시간 | 78.63ms |
| 최대 응답시간 | 284ms |
| 에러율 | 0%  |
| Throttle | 미발생 |

### 분석
- **콜드 스타트 해결**: EventBridge 웜업(5분 간격) 적용 → 첫 요청부터 즉시 응답
- **응답시간 안정화**: 기존 최대 6s 지연 제거, 최대 284ms 이내로 개선

---

## 🔥 트러블슈팅 (요약)

- Lambda 런타임 불일치로 인한 NetworkAccessForbidden → **베이스 이미지 수정**으로 해결
- Mangum lifespan 설정 오류로 인한 503 에러 → **`lifespan="off"` 옵션 추가**로 해결
- Docker 이미지 빌드 캐시 문제 → **캐시 제거 및 재빌드**로 해결
- AWS_REGION 예약어 충돌 → **커스텀 변수명(`MY_APP_REGION`)** 으로 변경
- Terraform state 관리 문제(EntityAlreadyExists) → **S3 Remote Backend 도입**으로 해결
- Lambda 콜드스타트 6s 지연 → EventBridge 웜업으로 해결

👉 상세 내용은 [포트폴리오](https://modifyc.github.io) 참고

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
├── my_terraform/            # Terraform IaC
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── .github/workflows/
│   ├── deploy.yaml          # SAM 자동 배포
│   └── terraform.yaml       # Terraform 자동 적용
└── README.md
```

---

## 👤 Author

- **이름**: 최수정
- **Portfolio**: [https://modifyc.github.io](https://modifyc.github.io)
- **Blog**: [https://cmod-ify.tistory.com/](https://cmod-ify.tistory.com/)