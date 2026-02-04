from fastapi import FastAPI, Request
from database import (
    get_or_create_malang,
    feed_malang,
    special_skill,
    get_malang_status,
    stroking_malang,
    clean_malang,
    get_malang_image,
    get_malang_description,
    get_room_rankings_top3,
    reset_malang_data,
)

app = FastAPI()


@app.post("/message")
async def kakao_skill(request: Request):
    # 1. 카카오 데이터 파싱
    data = await request.json()
    user_id = data["userRequest"]["user"]["id"]

    # room_id 추출 (없으면 개인방 처리)
    room_id = data["userRequest"].get("chatRoom", {}).get("id", f"personal_{user_id}")

    # 사용자가 입력한 말
    user_input = data["userRequest"]["utterance"].strip()
    # 닉네임 정하기
    nickname = data["userRequest"]["user"].get("properties", {}).get("nickname", "집사")

    # 2. 기본 변수 초기화
    msg = ""
    img_url = "https://raw.githubusercontent.com/MODIFYC/MalangMaker/main/images/default_image.png"
    title_text = f"🐾 {nickname}님의 말랑이"  # 기본 타이틀

    # 기본 버튼 리스트
    default_buttons = [
        {"label": "상태 확인하기👌", "action": "message", "messageText": "상태"},
        {"label": "말랑이 밥 주기 🥣", "action": "message", "messageText": "밥"},
        {"label": "필살기 쓰기⚡", "action": "message", "messageText": "기술"},
    ]
    buttons = default_buttons

    # ==========================================
    # 초기화 및 만렙 확인
    # ==========================================
    malang = get_or_create_malang(user_id, nickname)
    current_lvl = int(malang["level"])

    # 새로 분양
    if "분양" in user_input or "새로" in user_input:
        # database.py에 유저 삭제(또는 초기화) 함수를 호출
        msg, img_url = reset_malang_data(user_id)

    # 만렙 제한 로직 (밥, 쓰다듬기, 기술 방어)
    elif current_lvl >= 15 and user_input in ["밥", "쓰다듬기", "기술", "교감"]:
        msg = (
            "✨ [ 전 설 의 영 역 ] ✨\n\n"
            "이 말랑이는 이미 정점에 도달하여\n"
            "더 이상의 수행이 필요하지 않습니다.\n\n"
            "현재 상태를 유지하며 명예를 누리거나,\n"
            "새로운 말랑이를 분양받아보세요!"
        )
        img_url = get_malang_image(15, malang["type"])
        buttons = [
            {"label": "현재 상태 유지 👌", "action": "message", "messageText": "상태"},
            {
                "label": "새로 분양 받기 ✨",
                "action": "message",
                "messageText": "분양",
            },
            {"label": "명예의 전당 🏆", "action": "message", "messageText": "랭킹"},
        ]

    # ==========================================
    # 🎮 명령어 분기 처리
    # ==========================================
    # 1. 밥 주기
    elif "밥" in user_input:
        msg, img_url = feed_malang(user_id, room_id)
        if img_url and "dead" in img_url:
            buttons = [
                {
                    "label": "새로 입양하기 🌱",
                    "action": "message",
                    "messageText": "분양",
                }
            ]
        else:
            buttons = [
                {"label": "다른 밥 주기 🥣", "action": "message", "messageText": "밥"}
            ]
    # 2. 필살기
    elif "기술" in user_input or "필살기" in user_input:
        msg, img_url = special_skill(user_id, room_id)
        if img_url and "dead" in img_url:
            buttons = [
                {
                    "label": "새로 입양하기 🌱",
                    "action": "message",
                    "messageText": "분양",
                }
            ]
        else:
            buttons = [
                {"label": "상태 확인 👌", "action": "message", "messageText": "상태"}
            ]

    # 3. 쓰다듬기 (교감)
    elif "쓰다듬기" in user_input or "교감" in user_input:
        msg, img_url = stroking_malang(user_id, room_id)
        buttons = [
            {"label": "밥 주기 🥣", "action": "message", "messageText": "밥"},
            {"label": "상태 확인 👌", "action": "message", "messageText": "상태"},
        ]
    # 4. 청소하기
    elif "똥" in user_input or "청소" in user_input:
        msg, img_url = clean_malang(user_id, room_id)
        buttons = [
            {"label": "밥 주기 🥣", "action": "message", "messageText": "밥"},
            {"label": "상태 확인 👌", "action": "message", "messageText": "상태"},
        ]
    # 5. 랭킹 확인
    elif "랭킹" in user_input or "순위" in user_input:
        msg, img_url = get_room_rankings_top3(room_id)
        title_text = "🏆 실시간 채팅방 랭킹"  # 타이틀 변경
        buttons = [
            {"label": "내 상태 확인 👌", "action": "message", "messageText": "상태"}
        ]

    # 6. 상태 확인 (기본)
    elif "상태" in user_input:
        msg, img_url = get_malang_status(user_id)

    # 7. 예외 처리
    else:
        msg, img_url = get_malang_status(user_id)
        title_text = f"어서와! {nickname} 집사!"

    # ==========================================
    # 📤 최종 응답 조립 (TextCard)
    # ==========================================
    res_card = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "basicCard": {  # textCard에서 변경
                        "title": title_text,
                        "description": msg,
                        "thumbnail": {"imageUrl": img_url},
                        "buttons": buttons,
                    }
                }
            ]
        },
    }
    return res_card
