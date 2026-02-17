# 🍡 말랑이 메이커 (Malang Maker)
> **AWS DynamoDB와 Python 기반의 카카오톡 챗봇 육성 시뮬레이션 게임**
> 사용자가 카카오톡을 통해 자신만의 캐릭터 '말랑이'를 육성하는 게임형 챗봇입니다. 서버리스 지향 아키텍처를 기반으로 하며, 실시간 데이터 정합성과 사용자 경험(UX)을 극대화한 전광판 스타일 UI가 특징입니다.

<br>

## 🎮 주요 기능 및 UI (Screenshots)
<p align="center">
  <img src="https://github.com/user-attachments/assets/d43f528c-89a1-4234-a4e8-084dfe48fd47" width="250">
  <img src="https://github.com/user-attachments/assets/0b461d9a-cd00-4a67-9aec-153398dae973" width="250">
  <img src="https://github.com/user-attachments/assets/1cd8cfec-beea-498c-8be2-39d7597f7eb8" width="250">
</p>

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

## 🛠️ 기술적 고민 및 해결 (Technical Challenges)

<details>
<summary><b>상세 내용 보기 (Toggle)</b></summary>

1. **DB I/O 최적화 및 응답 지연 시간(Latency) 단축**
    * UpdateItem 연산 직후 메모리 내 변수를 활용하는 '단일 트랜잭션 내 응답 생성' 방식을 통해 응답 속도를 약 50% 이상 최적화했습니다.
2. **통신 규격 최적화 및 스키마 정합성 확보**
    * 모든 응답 포맷을 basicCard로 단일화하여 카카오톡 런타임 스키마 에러를 차단했습니다.
3. **데이터 정합성 확보**
    * In-place Update를 통해 액션 성공 시 DB 수치를 로컬 객체에 즉시 동적 갱신하여 별도 재조회 없이 실시간 수치를 전달합니다.
4. **사용자 경험(UX) 고도화**
    * 버튼 3개 제한을 극복하기 위해 Quick Replies(바로가기)를 동적으로 노출하는 컨텍스트 기반 UI를 설계했습니다.
</details>

<details>
<summary><b>📝 최근 업데이트 및 픽스 (Bug Fix Log)</b></summary>

* **사망 로직 개선**: 죽을 때 이미지 URL 반환 시 변수 설정 순서 오류를 해결했습니다.
* **데이터 정합성**: 필살기로 사망 시 다음 말랑이에게 이전 타입의 대사가 노출되지 않도록 '오리진 타입' 선언 로직을 추가했습니다.
* **UI 최적화**: 텍스트 길이에 따른 글자 짤림 현상을 카드 분할 방식으로 해결하고, 만렙 도달 시 불필요한 성장 버튼이 나오지 않도록 예외 처리했습니다.

</details>

---

## 👤 Author
* **이름**: 최수정
* **Blog**: [https://cmod-ify.tistory.com/](https://cmod-ify.tistory.com/)
* **Keywords**: AWS Solutions Architect, Backend Developer, Python Enthusiast