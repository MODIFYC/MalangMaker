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
    img_url = "https://t1.kakaocdn.net/open_chat/default_image.png"
    title_text = f"🐾 {nickname}님의 말랑이"  # 기본 타이틀

    # 기본 버튼 리스트
    default_buttons = [
        {"label": "상태 확인하기👌", "action": "message", "messageText": "상태"},
        {"label": "말랑이 밥 주기 🥣", "action": "message", "messageText": "밥"},
        {"label": "쓰다듬기 🫳", "action": "message", "messageText": "쓰다듬기"},
        {"label": "필살기 쓰기⚡", "action": "message", "messageText": "기술"},
    ]
    buttons = default_buttons

    # ==========================================
    # 🎮 명령어 분기 처리
    # ==========================================
    # 1. 밥 주기
    if "밥" in user_input:
        msg, img_url = feed_malang(user_id, room_id)
        if img_url and "dead" in img_url:
            buttons = [
                {
                    "label": "새로 입양하기 🌱",
                    "action": "message",
                    "messageText": "상태",
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
                    "messageText": "상태",
                }
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
    print(f"DEBUG: 최종 전송 이미지 URL -> {img_url}")
    return res_card
