from fastapi import FastAPI, Request
import json
import time
import hashlib

# region agent log helper
_AGENT_LOG_PATH = r"c:\Users\USER\MalangMaker\.cursor\debug.log"


def _agent_uid8(value) -> str:
    try:
        s = str(value).encode("utf-8", errors="ignore")
        return hashlib.sha256(s).hexdigest()[:8]
    except Exception:
        return "uid_err"


def _agent_log(
    *, runId: str, hypothesisId: str, location: str, message: str, data: dict
):
    try:
        payload = {
            "sessionId": "debug-session",
            "runId": runId,
            "hypothesisId": hypothesisId,
            "location": location,
            "message": message,
            "data": data,
            "timestamp": int(time.time() * 1000),
        }
        with open(_AGENT_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        # 로깅 실패는 서비스 동작에 영향 주지 않음
        pass


# endregion
from database import (
    get_or_create_malang,
    feed_malang,
    special_skill,
    get_malang_status,
    stroking_malang,
    clean_malang,
    get_malang_image,
    get_room_rankings_top3,
    reset_malang_data,
    get_malang_response_content,
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

    # 닉네임(칭호) 정하기
    nickname = data["userRequest"]["user"].get("properties", {}).get("nickname", "집사")

    # 2. 기본 변수 초기화
    msg = ""
    img_url = ""

    # 기본 버튼 리스트
    default_buttons = [
        {"label": "상태 확인하기👌", "action": "message", "messageText": "/상태"},
        {"label": "말랑이 밥 주기 🥣", "action": "message", "messageText": "/밥"},
    ]
    buttons = default_buttons

    # ==========================================
    # 초기화 및 만렙 확인
    # ==========================================
    malang = get_or_create_malang(user_id, nickname)
    current_lvl = int(malang["level"])
    origin_malang_type = malang["type"]

    # region agent log (H5)
    _agent_log(
        runId="run1",
        hypothesisId="H5",
        location="main.py:kakao_skill:after_parse",
        message="request parsed",
        data={
            "uid8": _agent_uid8(user_id),
            "room8": _agent_uid8(room_id),
            "utterance": user_input[:50],
            "nickname_present": bool(nickname),
        },
    )
    # endregion

    # region agent log (H2)
    _agent_log(
        runId="run1",
        hypothesisId="H2",
        location="main.py:kakao_skill:after_get_or_create",
        message="malang loaded",
        data={
            "uid8": _agent_uid8(user_id),
            "malang_keys": sorted(list(malang.keys()))[:25],
            "level_raw": str(malang.get("level")),
            "type_raw": str(malang.get("type")),
            "health_raw": str(malang.get("health")),
            "exp_raw": str(malang.get("exp")),
        },
    )
    # endregion

    quick_replies = []
    # 🎮 명령어 분기 처리
    if "/도움" in user_input or "/헬프" in user_input:
        msg = (
            "📜 [ 말랑메이커 이용 가이드 ]\n"
            "━━━━━━━━━━━━━━━━\n\n"
            "🥣 밥 주기\n"
            "ㄴ /밥 : 체력 회복 및 소량 경험치\n\n"
            "💕 쓰다듬기\n"
            "ㄴ /쓰다듬기 : 하루 한 번! 대박 경험치\n\n"
            "🧹 똥 치우기\n"
            "ㄴ /치우기 : 쾌적한 환경 (경험치 보너스)\n\n"
            "⚡ 필살기\n"
            "ㄴ /필살기 : 대박 성장 혹은... 무지개 다리 🎲\n\n"
            "🔍 상태 확인\n"
            "ㄴ /상태 : 현재 수치 및 모습 확인\n\n"
            "🏆 랭킹 보기\n"
            "ㄴ /랭킹 : 우리 방 TOP 3 말랑이\n\n"
            "🐣 새로 분양\n"
            "ㄴ /리셋 : 데이터 초기화 및 재시작\n\n"
            "━━━━━━━━━━━━━━━━\n"
            "💡 Tip: 하단의 버튼을 눌러보세요!"
        )
        # 도움말일 때만 하단 둥근 버튼(퀵리플라이) 추가
        quick_replies = [
            {"label": "밥 주기 🥣", "action": "message", "messageText": "/밥"},
            {"label": "쓰다듬기 💕", "action": "message", "messageText": "/쓰담"},
            {"label": "똥치우기 💩", "action": "message", "messageText": "/똥"},
            {"label": "필살기 ⚡", "action": "message", "messageText": "/기술"},
            {"label": "랭킹 보기 🏆", "action": "message", "messageText": "/랭킹"},
        ]
        return {
            "version": "2.0",
            "template": {
                "outputs": [{"simpleText": {"text": msg}}],
                "quickReplies": quick_replies,
            },
        }

    # 새로 분양 (가이드에 /리셋도 표기되어 있어 동일 처리)
    if "/분양" in user_input or "/리셋" in user_input:
        # region agent log (H6)
        _agent_log(
            runId="run1",
            hypothesisId="H6",
            location="main.py:kakao_skill:branch_reset",
            message="branch selected: reset/adopt",
            data={"uid8": _agent_uid8(user_id), "room8": _agent_uid8(room_id)},
        )
        # endregion
        try:
            msg, img_url = reset_malang_data(user_id, room_id)
            # region agent log (H6)
            _agent_log(
                runId="run1",
                hypothesisId="H6",
                location="main.py:kakao_skill:after_reset",
                message="reset returned",
                data={
                    "uid8": _agent_uid8(user_id),
                    "msg_len": len(msg or ""),
                    "msg_head": (msg or "")[:40],
                    "img_url_head": (img_url or "")[:60],
                    "img_url_empty": not bool(img_url),
                },
            )
            # endregion
        except Exception as e:
            # region agent log (H6)
            _agent_log(
                runId="run1",
                hypothesisId="H6",
                location="main.py:kakao_skill:reset_exception",
                message="exception in reset_malang_data call",
                data={
                    "uid8": _agent_uid8(user_id),
                    "err_type": type(e).__name__,
                    "err_msg": str(e)[:200],
                },
            )
            # endregion
            raise

    # 만렙 제한 로직 (밥, 쓰다듬기, 기술 방어)
    elif current_lvl >= 15 and user_input in ["/밥", "/쓰담", "/기술", "/교감"]:
        msg = (
            "✨ [ 전 설 의 영 역 ] ✨\n\n"
            "이 말랑이는 이미 정점에 도달하여\n"
            "더 이상의 수행이 필요하지 않습니다.\n\n"
            "현재 상태를 유지하며 명예를 누리거나,\n"
            "새로운 말랑이를 분양받아보세요!"
        )
        img_url = get_malang_image(15, malang["type"])
        buttons = [
            {
                "label": "새로 분양 받기 ✨",
                "action": "message",
                "messageText": "/분양",
            },
            {"label": "명예의 전당 🏆", "action": "message", "messageText": "/랭킹"},
        ]
    # 만렙 상태 버튼
    elif current_lvl >= 15 and user_input in ["/상태"]:
        img_url = get_malang_image(15, malang["type"])
        buttons = [
            {
                "label": "새로 분양 받기 ✨",
                "action": "message",
                "messageText": "/분양",
            },
            {"label": "명예의 전당 🏆", "action": "message", "messageText": "/랭킹"},
        ]
    # ==========================================
    # 🎮 명령어 분기 처리
    # ==========================================
    # 1. 밥 주기
    elif "/밥" in user_input:
        # region agent log (H5)
        _agent_log(
            runId="run1",
            hypothesisId="H5",
            location="main.py:kakao_skill:branch_feed",
            message="branch selected: feed",
            data={"uid8": _agent_uid8(user_id), "room8": _agent_uid8(room_id)},
        )
        # endregion
        msg, img_url = feed_malang(user_id, room_id)
        # region agent log (H4)
        _agent_log(
            runId="run1",
            hypothesisId="H4",
            location="main.py:kakao_skill:after_feed",
            message="feed returned",
            data={
                "uid8": _agent_uid8(user_id),
                "msg_len": len(msg or ""),
                "img_url_head": (img_url or "")[:60],
                "img_url_has_dead": bool(img_url and "dead" in img_url),
            },
        )
        # endregion
        if img_url and "dead" in img_url:
            buttons = [
                {
                    "label": "새로 입양하기 🌱",
                    "action": "message",
                    "messageText": "/분양",
                }
            ]
        else:
            buttons = [
                {
                    "label": "상태 확인 👌",
                    "action": "message",
                    "messageText": "/상태",
                },
                {
                    "label": "다른 밥 주기 🥣",
                    "action": "message",
                    "messageText": "/밥",
                },
            ]
    # 2. 필살기
    elif "/기술" in user_input or "/필살기" in user_input:
        msg, img_url = special_skill(user_id, room_id)
        if img_url and "dead" in img_url:
            buttons = [
                {
                    "label": "새로 입양하기 🌱",
                    "action": "message",
                    "messageText": "/분양",
                }
            ]
        else:
            buttons = [
                {
                    "label": "상태 확인 👌",
                    "action": "message",
                    "messageText": "/상태",
                },
                {
                    "label": "밥 주기 🥣",
                    "action": "message",
                    "messageText": "/밥",
                },
            ]

    # 3. 쓰다듬기 (교감)
    elif "/쓰담" in user_input or "/교감" in user_input:
        msg, img_url = stroking_malang(user_id, room_id)
        buttons = [
            {"label": "상태 확인 👌", "action": "message", "messageText": "/상태"},
            {"label": "밥 주기 🥣", "action": "message", "messageText": "/밥"},
        ]
    # 4. 청소하기
    elif "/똥" in user_input or "/청소" in user_input:
        msg, img_url = clean_malang(user_id, room_id)
        buttons = [
            {"label": "상태 확인 👌", "action": "message", "messageText": "/상태"},
            {"label": "밥 주기 🥣", "action": "message", "messageText": "/밥"},
        ]
    # 5. 랭킹 확인
    elif "/랭킹" in user_input or "/랭크" in user_input:
        msg, img_url = get_room_rankings_top3(room_id)
        buttons = [
            {"label": "내 상태 확인 👌", "action": "message", "messageText": "/상태"},
            {"label": "밥 주기 🥣", "action": "message", "messageText": "/밥"},
        ]

    # 6. 상태 확인 (기본)
    elif "/상태" in user_input:
        msg, img_url = get_malang_status(user_id)

    # 7. 예외 처리
    else:
        msg, img_url = get_malang_status(user_id)
        msg = (
            "📜 [ 말랑메이커 이용 가이드 ]\n"
            "━━━━━━━━━━━━━━━━\n\n"
            "🥣 밥 주기\n"
            "ㄴ /밥 : 체력 회복 및 소량 경험치\n\n"
            "💕 쓰다듬기\n"
            "ㄴ /쓰다듬기 : 하루 한 번! 대박 경험치\n\n"
            "🧹 똥 치우기\n"
            "ㄴ /치우기 : 쾌적한 환경 (경험치 보너스)\n\n"
            "⚡ 필살기\n"
            "ㄴ /필살기 : 대박 성장 혹은... 무지개 다리 🎲\n\n"
            "🔍 상태 확인\n"
            "ㄴ /상태 : 현재 수치 및 모습 확인\n\n"
            "🏆 랭킹 보기\n"
            "ㄴ /랭킹 : 우리 방 TOP 3 말랑이\n\n"
            "🐣 새로 분양\n"
            "ㄴ /리셋 : 데이터 초기화 및 재시작\n\n"
            "━━━━━━━━━━━━━━━━\n"
            "💡 Tip: 하단의 버튼을 눌러보세요!"
        )
        # 도움말일 때만 하단 둥근 버튼(퀵리플라이) 추가
        quick_replies = [
            {"label": "밥 주기 🥣", "action": "message", "messageText": "/밥"},
            {"label": "쓰다듬기 💕", "action": "message", "messageText": "/쓰담"},
            {"label": "똥치우기 💩", "action": "message", "messageText": "/똥"},
            {"label": "필살기 ⚡", "action": "message", "messageText": "/기술"},
            {"label": "랭킹 보기 🏆", "action": "message", "messageText": "/랭킹"},
        ]
        return {
            "version": "2.0",
            "template": {
                "outputs": [{"simpleText": {"text": msg}}],
                "quickReplies": quick_replies,
            },
        }

    # ==========================================
    # 📤 최종 응답 조립
    # ==========================================
    if img_url and "dead" in img_url:
        content = get_malang_response_content(user_id, origin_malang_type, True)
    else:
        content = get_malang_response_content(user_id, origin_malang_type)

    # 말랑이의 정보 (타이틀과 설명)
    malang_desc = content["description"]
    malang_title = content["title"]

    res_card = {
        "version": "2.0",
        "template": {
            "outputs": [
                {"simpleText": {"text": msg}},
                {
                    "basicCard": {
                        "title": malang_title,
                        "description": malang_desc,
                        "thumbnail": {"imageUrl": img_url},
                        "buttons": buttons,
                        "buttonLayout": "horizontal",
                    }
                },
            ]
        },
    }
    # region agent log (H7)
    _agent_log(
        runId="run1",
        hypothesisId="H7",
        location="main.py:kakao_skill:before_return",
        message="response assembled",
        data={
            "uid8": _agent_uid8(user_id),
            "utterance": user_input[:20],
            "msg_len": len(msg or ""),
            "img_url_head": (img_url or "")[:60],
            "buttons_cnt": len(buttons or []),
            "outputs_cnt": len(res_card.get("template", {}).get("outputs", [])),
            "has_itemCard": any(
                isinstance(o, dict) and "itemCard" in o
                for o in res_card.get("template", {}).get("outputs", [])
            ),
        },
    )
    # endregion
    return res_card
