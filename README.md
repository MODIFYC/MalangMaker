# 🍡 말랑이 메이커 (Malang Maker)
> **AWS DynamoDB와 Python 기반의 카카오톡 챗봇 육성 시뮬레이션 게임**

[![Project Status](https://img.shields.io/badge/Project-Malang_Maker-ff69b4?style=for-the-badge)](https://github.com/)
[![AWS DynamoDB](https://img.shields.io/badge/AWS-DynamoDB-4053D6?style=for-the-badge&logo=amazondynamodb)](https://aws.amazon.com/dynamodb/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)

## 📖 프로젝트 개요
말랑이 메이커는 사용자가 카카오톡을 통해 자신만의 캐릭터 '말랑이'를 육성하는 게임형 챗봇입니다. 서버리스 지향 아키텍처를 기반으로 하며, 실시간 데이터 정합성과 사용자 경험(UX)을 극대화한 **전광판 스타일 UI**가 특징입니다.

---

## 🎮 주요 기능 및 UI (Screenshots)

| 🍚 말랑이 밥주기 | 🏆 실시간 랭킹 시스템 | 📜 명령어 가이드 (UX) |
| :---: | :---: | :---: |
| <img src="https://github.com/user-attachments/assets/0ca90837-bb52-4cd8-b19e-91b8bfbfb6bd" width="250"> | <img src="https://github.com/user-attachments/assets/1ff79e2f-4aec-4911-ba8b-799a81ac3c31" width="250"> | <img src="https://github.com/user-attachments/assets/a20cb30d-f4ca-48f3-b58f-8bc33d63953d" width="250"> |


---

## 🏗️ 시스템 아키텍처 (Architecture)
본 프로젝트는 확장성과 비용 효율성을 최우선으로 고려하여 설계되었습니다.



* **Interface:** Kakao i OpenBuilder (Skill Server)
* **Backend:** FastAPI (Python 3.10+)
* **Database:** AWS DynamoDB (NoSQL - 고가용성 및 저지연 데이터 처리)
* **Infrastructure:** AWS IAM (최소 권한 원칙 적용), ngrok (Tunneling)

---

## 🚀 주요 기능 (Core Features)

* **실시간 육성 시스템**: 밥 주기, 쓰다듬기, 똥 치우기 등 상호작용을 통한 성장 로직.
* **동적 진화 로직**: 레벨에 따라 총 15단계의 이미지 및 수식어 변화 (Lv.15 전설의 말랑이 달성 가능).
* **채팅방별 랭킹 (Leaderboard)**: `room_id`를 기반으로 해당 채팅방 내 TOP 3 말랑이 실시간 정렬 및 출력.
* **고도화된 예외 처리**:
    * 하루 1회 교감 제한, 하루 2회 청소 제한 등 시간 기반 제어.
    * 필살기 사용 시 확률 기반 성공/사망(데이터 초기화) 로직.
    * 만렙(Lv.15) 달성 시 전설의 집사 칭호 및 인터페이스(버튼) 동적 변경.
* **도움말 및 UI**: `Quick Replies`를 활용한 명령어 가이드 및 `basicCard` 스키마 통일.

---

## 📂 프로젝트 구조

```text
MalangMaker/
├── main.py          # FastAPI 서버 및 카카오톡 스킬 엔드포인트 로직
├── database.py      # DynamoDB CRUD 및 게임 엔진 핵심 로직
├── images/          # 레벨별 말랑이 이미지 자산 관리
└── README.md        # 프로젝트 문서화
```
---

## 🛠️ 기술적 고민 및 해결 (Technical Challenges)
<details>
<summary><b>🛠 기술적 도전 (클릭하여 보기)</b></summary>

### 1. DB I/O 최적화 및 응답 지연 시간(Latency) 단축
* **문제:** 데이터 업데이트 후 최신 상태를 사용자에게 보여주기 위해 다시 `GetItem`을 호출할 경우, 빈번한 DB I/O 발생으로 인한 비용 증가 및 챗봇 응답 지연 우려.
* **해결:** `UpdateItem` 연산 직후 계산된 최신 수치를 메모리 내 변수에 즉시 할당하고, 이를 응답 메시지 조립에 활용하는 **'단일 트랜잭션 내 응답 생성'** 방식을 채택했습니다. 이를 통해 추가적인 읽기 요청 없이도 **응답 속도를 약 50% 이상 최적화**했습니다.


### 2. 통신 규격 최적화 및 스키마 정합성 확보
* **문제:** `textCard`와 `basicCard`를 혼용하거나, 특정 필드(Thumbnail, Buttons) 누락 시 카카오톡 클라이언트에서 "Must be of the same schema" 오류 및 응답 거부 현상 발생.
* **해결:** 모든 응답 포맷을 **`basicCard`로 단일화**하여 규격의 일관성을 확보했습니다. 특히 이미지가 없는 랭킹 등의 기능에서도 **기본 리소스 URL을 강제 할당**하는 예외 처리를 통해 런타임 스키마 에러를 완벽히 차단했습니다.


### 3. 데이터 정합성 확보 및 상태 갱신 로직 최적화
* **문제:** 밥 주기, 똥 치우기, 쓰다듬기, 필살기 등 각 액션 수행 시 DynamoDB에서 데이터를 읽어오는 시점과 로컬 객체를 갱신하는 시점이 맞지 않아, 이전 상태의 낡은 수치가 출력되거나 업데이트가 누락되는 정합성 오류 발생.
* **해결:**  **데이터 로드 객체 분리:** DB에서 원본 데이터를 가져오는 객체와 비즈니스 로직에서 가공되는 객체를 명확히 분리하여, 서로 다른 함수 호출 간에도 데이터가 섞이지 않도록 구조를 재설계했습니다.
    * **동적 상태 갱신(In-place Update):** 액션 성공 시 DB에 반영된 최신 수치를 로컬 객체에 즉시 동적 갱신(Dynamic Update)하여, 별도의 재조회 과정 없이도 사용자에게 항상 정확한 실시간 수치를 전달하도록 정합성을 확보했습니다.


### 4. 견고한 예외 처리 및 경계값 설계 (Boundary Cases)
* **문제:** 체력 100% 초과, 사망(데이터 삭제) 후 즉시 명령어 입력, 만렙 도달 후의 무의미한 성장 등 게임 밸런스 및 로직 붕괴 위협.
* **해결:**  **Clamping 로직:** `min(100, new_health)` 등을 적용해 모든 수치가 정의된 범위를 벗어나지 않도록 제어했습니다.
    * **상태 기반 가드(Guard Clause):** 명령어 진입점(Entry Point)에서 생존 여부와 레벨을 먼저 판별하여, 사망 유저에게는 '분양'을, 만렙 유저에게는 '전설의 집사' 전용 UI와 칭호를 제공하는 **조건부 인터페이스**를 구현했습니다.


### 5. 사용자 경험(UX) 고도화: 버튼 제약 극복
* **문제:** 카카오톡 출력 버튼이 3개로 제한되어 있어 다수의 명령어를 유저에게 직관적으로 전달하기 어려움.
* **해결:** `Quick Replies`(바로가기)를 특정 상황(도움말 요청 등)에서만 동적으로 팝업시키는 **컨텍스트 기반 UI**를 설계했습니다. 이를 통해 유틸리티 버튼과 핵심 게임 버튼을 분리하여 제한된 환경에서도 쾌적한 조작 환경을 제공했습니다.

</details>

---

### 👤 Author
* **이름:** 최수정

* **Blog:**  https://cmod-ify.tistory.com/

* **Keywords:** AWS Solutions Architect, Backend Developer, Python Enthusiast