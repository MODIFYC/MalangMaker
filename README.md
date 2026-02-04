# 🍡 말랑이 메이커 (Malang Maker)
> **AWS DynamoDB와 Python 기반의 카카오톡 챗봇 육성 시뮬레이션 게임**

[![Project Status](https://img.shields.io/badge/Project-Malang_Maker-ff69b4?style=for-the-badge)](https://github.com/)
[![AWS DynamoDB](https://img.shields.io/badge/AWS-DynamoDB-4053D6?style=for-the-badge&logo=amazondynamodb)](https://aws.amazon.com/dynamodb/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)

## 📖 프로젝트 개요
말랑이 메이커는 사용자가 카카오톡을 통해 자신만의 캐릭터 '말랑이'를 육성하는 게임형 챗봇입니다. **AWS SAA(Solutions Architect Associate)** 관점에서 설계된 서버리스 지향 아키텍처를 기반으로 하며, 실시간 데이터 정합성과 사용자 경험(UX)을 극대화한 **전광판 스타일 UI**가 특징입니다.

---

## 🏗️ 시스템 아키텍처 (Architecture)
본 프로젝트는 확장성과 비용 효율성을 최우선으로 고려하여 설계되었습니다.



* **Interface:** Kakao i OpenBuilder (Skill Server)
* **Backend:** FastAPI (Python 3.10+)
* **Database:** AWS DynamoDB (NoSQL - 고가용성 및 저지연 데이터 처리)
* **Infrastructure:** AWS IAM (최소 권한 원칙 적용), ngrok (Tunneling)

---

## ✨ 핵심 기능 (Core Features)

### 1️⃣ 전광판 스타일 UI
모든 응답은 `textCard` 형식을 사용하며, 가독성을 위해 특수문자와 여백을 활용한 '전광판 레이아웃'을 적용했습니다.
* **[ SUCCESS ]**: 밥 주기 성공 시 실시간 상태 정보 포함 출력
* **[ ULTIMATE ]**: 필살기 성공 시 화려한 시각적 피드백 제공
* **[ CRITICAL ERROR ]**: 리스크 발생 시 사망 및 데이터 삭제 효과 구현

### 2️⃣ 확률 기반 동적 로직 (Probabilistic Logic)
단순 반복형 게임을 탈피하기 위해 세밀한 확률 시스템을 도입했습니다.
* **0.5% 전설 확률**: '황금 만두' 당첨 시 즉시 레벨업 및 올스탯 회복 (희소성 기반 재미 부여)
* **15% 배탈 확률**: 상한 음식을 통한 체력 감소 리스크로 긴장감 유지

### 3️⃣ 하이 리스크-하이 리턴 '필살기'
* 현재 체력의 **80% 성공 확률** 로직 적용 (체력이 낮을수록 실패 확률 증가)
* 실패 시 **데이터 삭제(Hard Delete)** 정책을 통해 게임의 몰입도와 리스크 관리

---

## 🛠️ 기술적 고민 및 해결 (Technical Challenges)

### 🚀 데이터 처리 최적화 (Latency Reduction)
* **문제:** 빈번한 상태 갱신 요청으로 인한 DB I/O 비용 및 응답 지연 우려
* **해결:** `UpdateItem` 연산 직후 계산된 최신 수치를 즉시 리턴하여, 추가 `GetItem` 요청 없이 단일 트랜잭션 내에서 응답 메시지를 생성하도록 설계하여 **응답 속도를 최적화**했습니다.

### 🛡️ 클라우드 보안 관리
* **보안:** AWS Credentials를 코드에 노출하지 않고 `.env` 파일과 환경 변수를 통해 관리
* **IAM:** 최소 권한 원칙(Principle of Least Privilege)을 준수하여 특정 DynamoDB 테이블에만 접근 가능한 전용 정책 운영

---

## 📂 폴더 구조
```bash
.
├── main.py          # FastAPI 라우팅 및 카카오 스킬 엔드포인트
├── database.py      # AWS DynamoDB CRUD 및 게임 엔진 로직
└── requirements.txt  # 패키지 의존성 관리
```

### 👤 Author
* **이름:** 최수정

* **Blog:**  https://cmod-ify.tistory.com/

* **Keywords:** AWS Solutions Architect, Backend Developer, Python Enthusiast