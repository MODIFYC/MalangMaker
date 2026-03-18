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

## 🛠️ 기술적 도전 및 해결

<details>
<summary><b>1. 시스템 성능 및 DB 최적화 (Latency 50% 단축)</b></summary>

- **Issue**: 빈번한 DB I/O와 `Decimal` 타입 직렬화 문제로 인한 응답 지연 및 500 에러 발생.
- **Solution**:
  - `UpdateItem` 연산 직후 메모리 내 변수를 활용하는 **단일 트랜잭션 응답 생성** 방식으로 구조 개선.
  - DynamoDB 전용 `decimal_to_int` 유틸리티 함수 구현으로 데이터 정합성과 응답 속도 동시 확보.
- **Result**: 전체 API 응답 시간을 기존 대비 50% 이상 단축.
</details>

<details>
<summary><b>2. 데이터 정합성 및 동적 로직 고도화</b></summary>

- **Issue**: 액션 수행(환생/진화) 시 이전 상태값이 잔존하거나 실시간 수치가 미반영되는 현상.
- **Solution**:
  - **In-place Update**: DB 반영 성공 시 로컬 객체 수치를 즉시 동적 갱신하여 재조회 없이 최신 데이터 전달.
  - **오리진 타입 선언**: 필살기 사망 후 환생 시 이전 타입의 대사가 노출되지 않도록 초기화 로직 강화.
- **Result**: 다중 사용자 환경에서도 실시간 데이터 정합성 100% 보장.
</details>

<details>
<summary><b>3. 카카오톡 플랫폼 제한을 극복한 UX 설계</b></summary>

- **Issue**: 버튼 3개 제한 및 텍스트 길이 제한으로 인한 UI 가독성 저하.
- **Solution**:
  - **Context-aware UI**: 사용자의 현재 상태(레벨/보유 아이템)에 따라 Quick Replies를 동적으로 노출.
  - **카드 분할 방식**: 긴 텍스트 출력 시 자동 카드 슬라이싱 로직을 적용하여 글자 짤림 현상 방지.
- **Result**: 플랫폼 제약을 디자인 패턴으로 해결하여 사용자 경험 극대화.
</details>

---

## 👤 Author

- **이름**: 최수정
- **Blog**: [https://cmod-ify.tistory.com/](https://cmod-ify.tistory.com/)
- **Keywords**: AWS Solutions Architect, Backend Developer, Python Enthusiast