# main.py
from fastapi import FastAPI, Request
from database import (
    get_or_create_malang,
    update_health,
    feed_malang,
    special_skill,
    get_malang_status,
    stroking_malang,
    clean_malang,
)

app = FastAPI()


@app.post("/message")
async def kakao_skill(request: Request):
    data = await request.json()
    user_id = data["userRequest"]["user"]["id"]
    user_input = data["userRequest"]["utterance"].strip()  # 사용자가 입력한 말

    # 기본 버튼 리스트 (아무것도 해당 안 될 때)
    buttons = [
        {"label": "상태 확인하기👌", "action": "message", "messageText": "상태"},
        {"label": "말랑이 밥 주기 🥣", "action": "message", "messageText": "밥"},
        {"label": "쓰다듬기 🫳", "action": "message", "messageText": "쓰다듬기"},
        {"label": "필살기 쓰기⚡", "action": "message", "messageText": "기술"},
    ]

    if "밥" in user_input:
        # 1. 밥 먹기 로직 실행 및 결과 메시지(result_msg)와 현재 수치들 가져오기
        msg, current_hp = feed_malang(user_id)
        if current_hp <= 0:
            msg = f"💀 상한 음식을 먹고 말랑이가 결국 쓰러졌어... \n새로운 말랑이를 찾아보자."
            buttons = [
                {"label": "새로 시작하기", "action": "message", "messageText": "상태"}
            ]
        else:
            msg = msg
            buttons = [
                {"label": "다른 밥 주기 🥣", "action": "message", "messageText": "밥"}
            ]

    elif "기술" in user_input or "필살기" in user_input:
        result, error_msg = special_skill(user_id)
        if error_msg:
            msg = error_msg
            buttons = [
                {"label": "새로 키우기 🌱", "action": "message", "messageText": "상태"}
            ]
        else:
            msg = result["final_msg"]
            buttons = [
                {"label": "상태 확인 👌", "action": "message", "messageText": "상태"}
            ]
    elif "쓰다듬기" in user_input or "교감" in user_input:
        msg = stroking_malang(user_id)
        buttons = [
            {"label": "밥 주기 🥣", "action": "message", "messageText": "밥"},
            {"label": "상태 확인 👌", "action": "message", "messageText": "상태"},
        ]
    elif "똥" in user_input or "청소" in user_input:
        msg = clean_malang(user_id)
        buttons = [
            {"label": "밥 주기 🥣", "action": "message", "messageText": "밥"},
            {"label": "상태 확인 👌", "action": "message", "messageText": "상태"},
        ]

    elif "상태" in user_input:
        msg = get_malang_status(user_id)
        # 상태창에서는 모든 버튼 다 보여주기
        pass

    else:
        msg = ""

    # 최종 응답 구조 (TextCard 적용)
    return {
        "version": "2.0",
        "template": {
            "outputs": [{"textCard": {"description": msg, "buttons": buttons}}]
        },
    }
