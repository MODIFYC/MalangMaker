# 🍡 말랑이 메이커 (Malang Maker)
> **AWS DynamoDB와 Python 기반의 카카오톡 챗봇 육성 시뮬레이션 게임**
> 사용자가 카카오톡을 통해 자신만의 캐릭터 '말랑이'를 육성하는 게임형 챗봇입니다. 서버리스 지향 아키텍처를 기반으로 하며, 실시간 데이터 정합성과 사용자 경험(UX)을 극대화한 전광판 스타일 UI가 특징입니다.

<br>

## 🎮 주요 기능 및 UI (Screenshots)
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

## 🏗️ 시스템 아키텍처 (Architecture)
본 프로젝트는 확장성과 비용 효율성을 최우선으로 고려하여 설계되었습니다.
* **Interface**: Kakao i OpenBuilder (Skill Server)
* **Backend**: FastAPI (Python 3.10+)
* **Database**: AWS DynamoDB (NoSQL - 고가용성 및 저지연 데이터 처리)
* **Infrastructure**: AWS IAM (최소 권한 원칙 적용), ngrok (Tunneling)
* **Containerization**: Docker, Docker Compose (개발 환경 일관성 확보)



---

## 🚀 주요 기능 (Core Features)

* **실시간 육성 시스템**: 밥 주기, 쓰다듬기, 똥 치우기 등 상호작용을 통한 성장 로직.
* **동적 진화 로직**: 레벨에 따라 총 15단계의 이미지 및 수식어 변화 (Lv.15 전설의 말랑이 달성 가능).
* **채팅방별 랭킹 (Leaderboard)**: `room_id`를 기반으로 해당 채팅방 내 TOP 3 말랑이 실시간 정렬 및 출력.
* **고도화된 예외 처리**: 하루 1회 교감 제한, 필살기 사용 시 확률 기반 사망 로직, 만렙 전용 UI 제공 등.

---

## 📂 프로젝트 구조

MalangMaker/
```
├── main.py              # FastAPI 서버 및 카카오톡 스킬 엔드포인트 로직
├── database.py          # DynamoDB CRUD 및 게임 엔진 핵심 로직
├── descriptions.py      # 말랑이 타입별 대사 및 진화 데이터 관리
├── images/              # 레벨별 말랑이 이미지 자산 관리
├── Dockerfile           # 컨테이너 빌드 설정
├── docker-compose.yml   # 로컬 개발 및 배포 환경 자동화 설정
└── README.md            # 프로젝트 문서화
```
---

## 🛠️ 기술적 성장 및 문제 해결 (Technical Challenges & Fixes)

프로젝트를 개발하며 마주한 핵심 기술적 난제들과 이를 해결하며 최적화한 기록입니다.

<details>
<summary><b>1. 시스템 성능 및 DB 최적화 (Latency 50% 단축)</b></summary>

* **Issue**: 빈번한 DB I/O와 `Decimal` 타입 직렬화 문제로 인한 응답 지연 및 500 에러 발생.
* **Solution**: 
  - `UpdateItem` 연산 직후 메모리 내 변수를 활용하는 **'단일 트랜잭션 응답 생성'** 방식으로 구조 개선.
  - DynamoDB 전용 `decimal_to_int` 유틸리티 함수를 구현하여 데이터 정합성과 응답 속도를 동시에 확보.
* **Result**: 전체적인 API 응답 시간을 기존 대비 50% 이상 단축했습니다.
</details>

<details>
<summary><b>2. 데이터 정합성 및 동적 로직 고도화</b></summary>

* **Issue**: 액션 수행(환생/진화) 시 이전 상태값이 잔존하거나 실시간 수치가 미반영되는 현상.
* **Solution**: 
  - **In-place Update**: DB 반영 성공 시 로컬 객체 수치를 즉시 동적 갱신하여 재조회 없이 최신 데이터 전달.
  - **오리진 타입 선언**: 필살기 사망 후 환생 시 이전 타입의 대사가 노출되지 않도록 초기화 로직 강화.
* **Result**: 다중 사용자가 접속하는 환경에서도 실시간 데이터 정합성을 100% 보장합니다.
</details>

<details>
<summary><b>3. 카카오톡 플랫폼 제한을 극복한 UX 설계</b></summary>

* **Issue**: 버튼 3개 제한 및 텍스트 길이 제한으로 인한 UI 가독성 저하.
* **Solution**: 
  - **Context-aware UI**: 사용자의 현재 상태(레벨/보유 아이템)에 따라 **Quick Replies(바로가기)**를 동적으로 노출.
  - **카드 분할 방식**: 긴 텍스트 출력 시 자동 카드 슬라이싱 로직을 적용하여 글자 짤림 현상 방지.
* **Result**: 플랫폼의 제약 사항을 디자인 패턴으로 해결하여 사용자 경험을 극대화했습니다.
</details>

---

## 👤 Author
* **이름**: 최수정
* **Blog**: [https://cmod-ify.tistory.com/](https://cmod-ify.tistory.com/)
* **Keywords**: AWS Solutions Architect, Backend Developer, Python Enthusiast