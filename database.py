# region agent log helper
import json
import time
import hashlib

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
        pass


# endregion
# ==========================================
# ⚙️ 1. 초기 설정 및 환경 변수 (CONFIG)
# ==========================================
import boto3
import os
import random
from dotenv import load_dotenv
from decimal import Decimal
from datetime import datetime
import random
from descriptions import get_malang_data, USER_TITLES, MALANG_CONFIG

load_dotenv()

# DynamoDB 접속 설정
dynamodb = boto3.resource(
    "dynamodb",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION"),
)
table = dynamodb.Table("MalangUsers")


# ==========================================
# 🛠️ 2. 유틸리티 함수 (UTILITIES)
# - 이미지 매칭, 묘사 생성 등 보조 도구
# ==========================================
# 말랑이 이미지 매칭 함수
def get_malang_image(level, malang_type="typeA", is_dead=False):
    # 레벨 제한 (1~15)
    img_num = max(1, min(15, int(level)))

    # 깃허브 Raw 이미지 기본 경로
    base_url = "https://raw.githubusercontent.com/MODIFYC/MalangMaker/main/images"

    # 만약 죽은 상태라면 해당 타입 폴더의 dead.png 리턴
    if is_dead:
        return f"{base_url}/{malang_type}/dead.png"

    # 파일명 규칙: typeA/1.png
    image_url = f"{base_url}/{malang_type}/{img_num}.png"

    return image_url


# 시스템 이미지 매칭 함수
def get_system_image(filename):
    base_url = (
        "https://raw.githubusercontent.com/MODIFYC/MalangMaker/main/images/system"
    )
    return f"{base_url}/{filename}.png"


# 레벨별 묘사
def get_malang_response_content(user_id, m_type, is_dead=False):
    # 1. DB에서 유저 정보 조회
    malang = get_or_create_malang(user_id)
    lvl = int(malang.get("level", 1))

    if not is_dead:
        m_type = malang.get("type", "typeA")

    nickname = malang.get("nickname", "집사")

    # 2. 전용 모듈에서 텍스트 데이터 가져오기
    title_tag, desc = get_malang_data(m_type, lvl, is_dead)
    emoji = title_tag[-1]  # 맨 뒤 한 글자 (이모지)

    return {
        "title": f"{emoji} {nickname}의 {title_tag}",
        "description": desc,
    }


# 타입 변환 함수
def decimal_to_int(val):
    if isinstance(val, Decimal):
        return int(val)
    return val


# ==========================================
# 💾 3. 코어 데이터 로직 (CORE DATA)
# - 유저 생성 및 조회 (room_id 연동 필수)
# ==========================================
# 말랑이 가져오기 및 추가
def get_or_create_malang(user_id, nickname="집사"):
    # 1. 유저가 이미 있는지 확인
    response = table.get_item(Key={"user_id": user_id})
    if "Item" in response:
        item = response["Item"]
        # high_level 가져오기 (숫자일 수도, "none"일 수도 있음)
        hl = item.get("high_level", "none")
        if isinstance(hl, Decimal):
            hl = int(hl)
        return {
            "user_id": item.get("user_id"),
            "nickname": item.get("nickname", nickname),
            "malang_name": item.get("malang_name", "그냥 말랑이"),
            "type": item.get("type", "typeA"),
            "level": int(decimal_to_int(item.get("level", 1))),
            "health": int(decimal_to_int(item.get("health", 100))),
            "exp": int(decimal_to_int(item.get("exp", 0))),
            "clean_count": int(decimal_to_int(item.get("clean_count", 0))),
            "room_id": item.get("room_id", "none") or "none",
            "last_stroking_malang": item.get("last_stroking_malang", "none") or "none",
            "last_clean_date": item.get("last_clean_date", "none") or "none",
            "high_level": hl,
        }

    new_malang = {
        "user_id": user_id,
        "nickname": nickname,
        "malang_name": "그냥 말랑이",
        "type": random.choice(["typeA", "typeB", "typeC"]),
        "level": 1,
        "health": 100,
        "exp": 0,
        "room_id": "none",
        "last_stroking_malang": "none",
        "last_clean_date": "none",
        "clean_count": 0,
        "high_level": 1,
    }
    table.put_item(Item=new_malang)
    return new_malang


# DB 업데이트
def update_malang_status(user_id, **kwargs):
    update_parts = []
    expression_values = {}
    expression_names = {}

    for key, value in kwargs.items():
        # 'level'은 DynamoDB 예약어라 별도 처리 필요
        if key in ["level", "type"]:
            alias = f"#{key[:3]}"  # #lev, #typ 식으로 별칭 생성
            update_parts.append(f"{alias} = :{key}")
            expression_values[f":{key}"] = value
            expression_names[alias] = key
        else:
            update_parts.append(f"{key} = :{key}")
            expression_values[f":{key}"] = value

    update_expression = "SET " + ", ".join(update_parts)

    table.update_item(
        Key={"user_id": user_id},
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_values,
        ExpressionAttributeNames=expression_names if expression_names else None,
    )


# 말랑이 새로 분양받기
def reset_malang_data(user_id, room_id):
    try:
        new_type = random.choice(["typeA", "typeB", "typeC"])

        # region agent log (H6)
        _agent_log(
            runId="run1",
            hypothesisId="H6",
            location="database.py:reset_malang_data:entry",
            message="reset entry",
            data={
                "uid8": _agent_uid8(user_id),
                "room8": _agent_uid8(room_id),
                "new_type": new_type,
            },
        )
        # endregion

        initial_title, _ = get_malang_data(new_type, 1)

        malang = get_or_create_malang(user_id)
        nickname = malang.get("nickname", "집사")
        high_level = malang.get("high_level", "none")

        reset_data = {
            "nickname": nickname,
            "malang_name": initial_title,
            "type": new_type,
            "level": 1,
            "health": 100,
            "exp": 0,
            "room_id": room_id,
            "last_stroking_malang": "none",
            "last_clean_date": "none",
            "clean_count": 0,
            "high_level": high_level,
        }

        update_malang_status(user_id, **reset_data)

        msg = (
            "🐣 [ 새 로 운 인 연 ]\n"
            "━━━━━━━━━━━━━━━━\n\n"
            "새로운 알이 도착했습니다!\n"
            f"이번엔 {initial_title}의 기운이 느껴지네요.\n\n"
            "어떤 모습으로 성장할지 기대해봐도 좋겠어요!"
        )

        img_url = get_malang_image(1, new_type)
        # region agent log (H6)
        _agent_log(
            runId="run1",
            hypothesisId="H6",
            location="database.py:reset_malang_data:success",
            message="reset success",
            data={
                "uid8": _agent_uid8(user_id),
                "new_type": new_type,
                "msg_len": len(msg),
                "img_url_head": (img_url or "")[:60],
            },
        )
        # endregion
        return msg, img_url
    except Exception as e:
        # region agent log (H6)
        _agent_log(
            runId="run1",
            hypothesisId="H6",
            location="database.py:reset_malang_data:exception",
            message="reset exception",
            data={
                "uid8": _agent_uid8(user_id),
                "err_type": type(e).__name__,
                "err_msg": str(e)[:200],
            },
        )
        # endregion
        print(f"Error: {e}")  # 로그 확인용
        return f"분양 과정에서 오류가 발생했어요: {e}", ""


# ==========================================
# 🎮 4. 말랑이 육성 액션 (USER ACTIONS)
# - 밥 주기, 교감, 똥 치우기, 필살기
# ==========================================
# 말랑이 먹이주기
def feed_malang(user_id, room_id):
    try:
        malang = get_or_create_malang(user_id)
        rand_val = random.random()  # 0.0 ~ 1.0 사이의 랜덤값

        # region agent log (H2)
        _agent_log(
            runId="run1",
            hypothesisId="H2",
            location="database.py:feed_malang:entry",
            message="feed_malang entry",
            data={
                "uid8": _agent_uid8(user_id),
                "room8": _agent_uid8(room_id),
                "malang_keys": sorted(list(malang.keys()))[:25],
                "level_raw": str(malang.get("level")),
                "type_raw": str(malang.get("type")),
                "health_raw": str(malang.get("health")),
                "exp_raw": str(malang.get("exp")),
            },
        )
        # endregion

        new_health = int(malang["health"])
        new_level = int(malang["level"])
        new_exp = int(malang["exp"])
        malang_type = malang.get("type", "typeA")
        malang_display_name = malang.get("malang_name", "말랑이")

        # region agent log (H1)
        _agent_log(
            runId="run1",
            hypothesisId="H1",
            location="database.py:feed_malang:before_config",
            message="type/config check",
            data={
                "uid8": _agent_uid8(user_id),
                "malang_type": str(malang_type),
                "type_in_config": bool(malang_type in MALANG_CONFIG),
                "rand_val": rand_val,
            },
        )
        # endregion

        malang_name = MALANG_CONFIG.get(malang_type, MALANG_CONFIG[malang_type])[
            "status"
        ]

        # 1. 상황별 랜덤 대사 리스트
        normal_feedback = [
            "✨ (와구와구) 냠냠! {malang_name}가 {food_name}을(를) 먹고 꼬리를 살랑살랑 흔들고 있어! 🐾",
            "🍬 말랑말랑! {food_name}은(는) 정말 꿀맛이래! {malang_name}의 눈이 반짝반짝 빛나고 있어! 👀✨",
            "🎈 퐁신퐁신~ {food_name}을(를) 먹더니 {malang_name}의 몸이 더 부풀어 올랐어! 기분 최고! 🌈",
            "🍭 {malang_name}가 {food_name}을(를) 소중하게 꼭 껴안고 먹고 있어! 너무 행복해 보여! 🥰",
            "🧁 달콤한 {food_name} 냄새가 솔솔~ {malang_name}가 기분이 좋아서 노래를 흥얼거려! 🎵",
        ]
        bad_feedback = [
            "🤢 으아앙! 상한 밥이었나봐... {malang_name} 얼굴이 파랗게 질려서 부들부들 떨고 있어... 🚑💨",
            "🍄 꾸르륵... {malang_name} 배에서 이상한 소리가 나! '말랑... 살려줘...' 라고 하는 것 같아... 😿",
            "⛈️ 콰광! 잘못된 식사였어! {malang_name}가 구석에 웅크리고 시무룩해졌어... 미안해 말랑아! 💔",
            "😵 {malang_name}가 갑자기 핑글핑글 돌더니 털썩 주저앉았어! 배가 많이 아픈가 봐... 🌪️",
            "🧼 퉤퉤! 비누 맛이 나는 밥이었나? {malang_name} 눈물 한 방울을 툭 흘렸어... 💧",
        ]
        legend_feedback = [
            "🏆 [LEGEND] 헉! {malang_name} 전설의 황금 만두를 한입에 꿀꺽! 갑자기 온몸에서 무지개색 광채가 뿜어져 나와! 🌟🦁🔥",
            "👑 웅장한 음악이 들려...! 전설의 만두 파워로 {malang_name} 초사이어인(?)이 되었어! 레벨업 가즈아! 🚀💫",
            "🪐 우주의 기운이 말랑이에게! 전설의 만두를 먹은 {malang_name} 공중에 붕 떠올라 빛나고 있어! 🌌✨",
        ]

        # 2. 확률별 로직 처리
        # [0.5% 확률] 전설의 만두 (희귀!!)
        if rand_val < 0.005:
            # region agent log (H1)
            _agent_log(
                runId="run1",
                hypothesisId="H1",
                location="database.py:feed_malang:branch",
                message="branch selected: legend",
                data={"uid8": _agent_uid8(user_id), "rand_val": rand_val},
            )
            # endregion
            new_level += 1
            new_health = 100
            new_exp = 0
            header = "💎👑 [ L E G E N D ] 👑💎"
            body_msg = random.choice(legend_feedback).format(
                malang_name=malang_display_name
            )
            footer = "🌟 전설의 {malang_name} 탄생했습니다!".format(
                malang_name=malang_display_name
            )

        # [15% 확률] 상한 밥 (실패!!)
        elif rand_val < 0.155:
            # region agent log (H1)
            _agent_log(
                runId="run1",
                hypothesisId="H1",
                location="database.py:feed_malang:branch",
                message="branch selected: bad",
                data={"uid8": _agent_uid8(user_id), "rand_val": rand_val},
            )
            # endregion
            damage = random.randint(15, 30)
            new_health -= damage
            header = "💀⛈️ [ F A I L ] ⛈️💀"
            body_msg = random.choice(bad_feedback).format(
                malang_name=malang_display_name
            )
            footer = "💊 {malang_name} 상태가 이상해요...".format(
                malang_name=malang_display_name
            )

        # [그 외] 무난한 밥 (성공!!)
        else:
            # region agent log (H1)
            _agent_log(
                runId="run1",
                hypothesisId="H1",
                location="database.py:feed_malang:branch",
                message="branch selected: normal",
                data={"uid8": _agent_uid8(user_id), "rand_val": rand_val},
            )
            # endregion
            normal_foods = [
                {"name": "고소한 콩떡", "heal": 10, "exp": 15},
                {"name": "달콤한 꿀단지", "heal": 20, "exp": 10},
                {"name": "신선한 산딸기", "heal": 15, "exp": 12},
            ]
            food = random.choice(normal_foods)
            new_health += food["heal"]
            new_exp += food["exp"]
            header = "✨ 🎊 [ SUCCESS ] 🎊 ✨"
            body_msg = random.choice(normal_feedback).format(
                malang_name=malang_display_name, food_name=food["name"]
            )
            footer = ""

        # 3. 사망 시 처리
        if new_health <= 0:
            dead_title = get_malang_data(malang_type, new_level, is_dead=True)[0]

            reset_data = {
                "health": 0,
                "exp": 0,
                "level": 1,
                "type": "none",
                "malang_name": dead_title,
            }
            update_malang_status(user_id, **reset_data)

            # 2. 터진 이미지 URL 설정 (dead.png)
            dead_image_url = get_malang_image(new_level, malang_type, True)

            # 3. 유언(?) 메시지 조립
            header = "☠️🌫️ [ G A M E O V E R ] 🌫️☠️"
            body_msg = (
                f"상한 음식을 먹은 {malang_display_name}가\n"
                f"부들부들 떨더니...\n\n"
                f"펑!!! 하고 터져버렸습니다... 👻"
            )
            footer = "🥀 새로운 말랑이를 입양해주세요..."

            final_msg = (
                f"{header}\n\n"
                f"{body_msg}\n\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"📉 최종 레벨: Lv.{malang['level']}\n"
                f"━━━━━━━━━━━━━━━━\n\n"
                f"{footer}"
            )

            # 사망했으므로 업데이트 없이 바로 리턴
            return final_msg, dead_image_url

        # 4. 생존 시 처리
        new_health = min(100, new_health)
        lv_up_msg = ""
        if new_exp >= 100:
            new_level += 1
            new_exp -= 100
            new_health = 100
            body_msg += "\n\n✨ [LEVEL UP]\n경험치가 꽉 차서 레벨업했어!"

        # 이미지 & 설명 가져오기
        image_url = get_malang_image(new_level, malang_type)

        # 5. 최종 메시지 조립 (여백과 줄바꿈 강조)
        final_msg = (
            f"{header}\n\n"
            f"{body_msg}{lv_up_msg}\n\n"
            f"⭐ Lv.{new_level} | {new_exp}%\n"
            f"❤️ 체력: {new_health}%\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"{footer}"
        )

        # 1. 일단 업데이트할 기본 항목 담기
        update_data = {
            "health": new_health,
            "exp": new_exp,
            "level": new_level,
            "room_id": room_id,
            "malang_name": get_malang_data(malang_type, new_level)[0],
        }

        # 2. 만약 만렙(15) 찍었다면 칭호 데이터도 추가
        if new_level >= 15:
            prefix = USER_TITLES.get(malang_type, "default")

            # 바구니에 칭호 정보 추가
            update_data["nickname"] = prefix

        # 3. DB 업데이트는 딱 한 번만!
        update_malang_status(user_id, **update_data)

        return final_msg, image_url
    except Exception as e:
        # region agent log (H3)
        _agent_log(
            runId="run1",
            hypothesisId="H3",
            location="database.py:feed_malang:exception",
            message="exception in feed_malang",
            data={
                "uid8": _agent_uid8(user_id),
                "err_type": type(e).__name__,
                "err_msg": str(e)[:200],
            },
        )
        # endregion
        raise


# 교감하기
def stroking_malang(user_id, room_id):
    malang = get_or_create_malang(user_id)

    # 오늘 날짜 구하기 (YYYY-MM-DD)
    today = datetime.now().strftime("%Y-%m-%d")
    last_date = malang.get("last_stroking_malang", "")
    print(f"DEBUG DB DATA: {malang}")
    malang_type = malang.get("type", "typeA")

    new_level = int(malang["level"])
    new_exp = int(malang["exp"])
    new_health = int(malang["health"])

    # 1. 이미 오늘 교감했다면?
    if last_date == today:
        header = "🐾✨ [ R E J E C T ] ✨🐾"
        body_msg = (
            f"말랑이는 이미 충분히 사랑받았어요!\n\n"
            f"지금은 기분 좋게 낮잠을 자고 있네요.\n"
            f"내일 다시 쓰다듬어주세요! 💤"
        )
        footer = "🌙 말랑이가 꿈속에서 당신을 만난대요."
        image_url = get_malang_image(new_level, malang_type)

    # 2. 오늘 처음 교감하는 거라면?
    else:
        # 보상 설정 (체력 30 회복, 경험치 20 획득)
        new_health = min(100, int(malang["health"]) + 30)
        new_exp = int(malang["exp"]) + 20
        new_level = int(malang["level"])
        malang_name = malang.get(malang_type, "말랑이")

        # 레벨업 체크
        if new_exp >= 100:
            new_level += 1
            new_exp -= 100
            new_health = 100

        # 1. 일단 업데이트할 기본 항목 담기
        malang_title_tag = get_malang_data(malang_type, new_level)[0]

        update_data = {
            "health": new_health,
            "exp": new_exp,
            "level": new_level,
            "room_id": room_id,
            "malang_name": malang_title_tag,  # 레벨업 대비 실시간 타이틀 갱신
            "last_stroking_malang": today,  # 쓰다듬기 날짜 기록
        }

        # 2. 만렙(15) 찍었다면 칭호 데이터도 추가
        if new_level >= 15:
            prefix = USER_TITLES.get(malang_type, "전설의 집사")
            update_data["nickname"] = prefix

        # 3. DB 업데이트는 한 번만!
        update_malang_status(user_id, **update_data)

        header = "🌕🛏️ [ C O M F O R T ] 🛏️🌕"
        body_msg = (
            f"{malang_name} 따뜻한 손길이 닿았습니다!\n\n"
            f"{malang_name}  기분이 좋아져서 몸을 배베 꼬며\n"
            f"{malang_name} 당신의 손에 머리를 부비적거려요! 😍"
        )
        footer = "📈 체력 +30 / 경험치 +20 보너스!"
        image_url = get_malang_image(new_level, malang_type)

    # 최종 메시지 조립
    final_msg = (
        f"{header}\n\n"
        f"{body_msg}\n\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"⭐ Lv.{malang['level'] if last_date == today else new_level} | {malang['exp'] if last_date == today else new_exp}%\n"
        f"❤️ 체력: {malang['health'] if last_date == today else new_health}%\n"
        f"━━━━━━━━━━━━━━━━\n\n"
        f"{footer}"
    )

    return final_msg, image_url


# 똥치우기
def clean_malang(user_id, room_id):
    malang = get_or_create_malang(user_id)
    today = datetime.now().strftime("%Y-%m-%d")

    # DB에서 날짜와 횟수 가져오기 (없으면 초기값)
    last_date = malang.get("last_clean_date", "")
    clean_count = int(malang.get("clean_count", 0))
    malang_type = malang.get("type", "typeA")

    # 날짜가 바뀌었으면 횟수 초기화
    if last_date != today:
        clean_count = 0

    msg_result = ""
    new_health = int(malang["health"])
    new_exp = int(malang["exp"])
    new_level = int(malang["level"])

    # 1. [1회차] 아침의 대청소
    if clean_count == 0:
        new_health = min(100, new_health + 20)
        new_exp += 15
        clean_count = 1
        header = "💩🧹 [ 1st S W E E P ] 🧹💩"
        body_msg = (
            "밤새 {malang_name}(이)가 엄청난 걸 생산해놨군요!\n\n"
            "코를 막고 구석구석 깨끗이 치웠습니다.\n"
            "{malang_name}(이)가 부끄러운지 몸을 숨기네요. 🫣"
        )
        footer = "🎁 대청소 보상: 체력 +20 / 경험치 +15"

    # 2. [2회차] 오후의 깔끔관리
    elif clean_count == 1:
        new_health = min(100, new_health + 10)
        new_exp += 5
        clean_count = 2
        header = "✨🧼 [ 2nd S W E E P ] 🧼✨"
        body_msg = (
            "오후에 생긴 작은 흔적까지 깔끔하게!\n\n"
            "환경이 쾌적해지자 말랑이가\n"
            "기분이 좋아져서 퐁신퐁신하게 부풀어 올랐어요! 🎈"
        )
        footer = "🍀 관리 보상: 체력 +10 / 경험치 +5"

    # 3. [회수 초과] 이미 너무 깨끗함
    else:
        header = "🚫🌈 [ P E R F E C T ] 🌈🚫"
        body_msg = (
            "{malang_name} 집에서 빛이 나고 있어요!\n\n"
            "이미 오늘 두 번이나 청소하셨잖아요.\n"
            "내일 다시 똥이 쌓이길 기다려주세요! 💤"
        )
        footer = ""

    # 레벨업 체크 및 DB 업데이트 로직
    lv_up_msg = ""
    if new_exp >= 100:
        new_level += 1
        new_exp -= 100
        new_health = 100
        lv_up_msg = "\n✨ [LEVEL UP] \n한계를 돌파하여 레벨업했습니다!"

    # 최종 메시지 조립
    image_url = get_malang_image(new_level, malang_type)

    final_msg = (
        f"{header}\n\n"
        f"{body_msg}{lv_up_msg}\n\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"⭐ Lv.{new_level} | {new_exp}%\n"
        f"❤️ 체력: {new_health}%\n"
        f"━━━━━━━━━━━━━━━━\n\n"
        f"{footer}"
    )

    # 1. 말랑이 타이틀 실시간 조립
    malang_title_tag = get_malang_data(malang_type, new_level)[0]

    # 2. 업데이트 바구니 구성
    update_data = {
        "health": new_health,
        "exp": new_exp,
        "level": new_level,
        "room_id": room_id,
        "malang_name": malang_title_tag,
        "last_clean_date": today,
        "clean_count": clean_count,
    }

    # 3. 만렙(15) 달성 시 칭호(닉네임) 업데이트
    if new_level >= 15:
        prefix = USER_TITLES.get(malang_type, "전설의 청소부")
        update_data["nickname"] = prefix

    # 4. DB 업데이트는 깔끔하게 한 번!
    update_malang_status(user_id, **update_data)

    return final_msg, image_url


# 필살기
def special_skill(user_id, room_id):
    malang = get_or_create_malang(user_id)
    current_hp = int(malang["health"])
    malang_type = malang["type"]

    # [방어 로직] 체력이 너무 낮으면 기술 사용 불가
    if current_hp <= 5:
        msg = "⚠️ 체력이 너무 부족하여 필살기를 쓸 수 없습니다! 먼저 밥을 주세요."
        img_url = get_malang_image(malang["level"], malang_type)
        return msg, img_url

    current_exp = int(malang["exp"])
    current_lvl = int(malang["level"])
    name = malang.get("name", "말랑이")
    current_type = malang.get("type", "typeA")
    nickname = malang.get("nickname", "집사")
    image_url = get_malang_image(current_lvl, current_type)

    # 성공 확률은 현재 체력의 80% 정도
    success_rate = current_hp * 0.8
    is_success = random.randint(1, 100) <= success_rate

    # 1. [실패] 말랑이가 버티지 못하고 터짐 💀
    if not is_success:
        # 유저가 키우던 타입에 맞는 죽음 이미지 매칭 (예: typeB_dead.png)
        dead_image_url = get_malang_image(current_lvl, current_type, True)

        header = "🚨🧨 [ CRITICAL ERROR ] 🧨🚨"
        body_msg = (
            f"💥 콰광!!! 에너지가 폭주합니다!\n\n"
            f"{nickname}님의 {name}가 무리하게 기술을 시도하다가\n"
            f"에너지를 견디지 못하고 산산조각 났습니다... 👻"
        )
        footer = "💀 말랑이의 명복을 빕니다"

        final_msg = (
            f"{header}\n\n"
            f"{body_msg}\n\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"📉 최종 레벨: Lv.{current_lvl}\n"
            f"━━━━━━━━━━━━━━━━\n\n"
            f"{footer}"
        )

        reset_malang_data(user_id, room_id)

        return final_msg, dead_image_url

    # 2. [성공] 체력을 소모하며 강력한 기술 발동! 🔥
    damage = current_hp // 2
    gain_exp = random.randint(40, 70)

    new_health = current_hp - damage
    new_exp = current_exp + gain_exp
    new_level = current_lvl

    lv_up_msg = ""
    if new_exp >= 100:
        new_level += 1
        new_exp -= 100
        new_health = 100
    lv_up_msg = "\n✨ [LEVEL UP] \n한계를 돌파하여 레벨업했습니다!"
    image_url = get_malang_image(new_level, current_type)
    header = "🔥⚡ [ U L T I M A T E ] ⚡🔥"
    body_msg = (
        f"⚔️ {name}의 필살기 전개!!\n\n"
        f"강력한 일격으로 주변이 진동합니다!\n"
        f"힘을 쏟아부은 {name}가 가쁜 숨을 쉽니다.{lv_up_msg}"
    )
    footer = "💪 다음 기술을 위해 체력을 회복하세요!"

    final_msg = (
        f"{header}\n\n"
        f"{body_msg}\n\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"⭐ Lv.{new_level} | {new_exp}%\n"
        f"❤️ 남은 체력: {new_health}%\n"
        f"━━━━━━━━━━━━━━━━\n\n"
        f"{footer}"
    )

    # 1. 생존 성공! 현재 레벨에 맞는 타이틀 가져오기
    malang_title_tag = get_malang_data(malang_type, new_level)[0]

    # 2. 업데이트 바구니 구성
    update_data = {
        "health": new_health,
        "exp": new_exp,
        "level": new_level,
        "room_id": room_id,
        "malang_name": malang_title_tag,
    }

    # 3. 만렙(15) 달성 시 칭호 업데이트
    if new_level >= 15:
        prefix = USER_TITLES.get(malang_type, "default")
        update_data["nickname"] = prefix

    # 4. DB 업데이트는 깔끔하게 한 번!
    update_malang_status(user_id, **update_data)

    return final_msg, image_url


# ==========================================
# 📊 5. 정보 조회 및 랭킹 (INFO & RANK)
# - 상태 확인, 랭킹 시스템
# ==========================================
# 상태 확인하기
def get_malang_status(user_id):
    malang = get_or_create_malang(user_id)

    # DB 값을 int로 안전하게 변환
    level = int(malang["level"])
    health = int(malang["health"])
    exp = int(malang["exp"])
    name = malang.get("name", "말랑이")

    # 말랑이의 랜덤 기분 대사
    feelings = [
        f"✨ {name}가 당신을 보며 꼬리를 흔들고 있어요!",
        f"💤 {name}가 기분 좋게 낮잠을 자고 싶어 해요.",
        f"🎵 {name}가 콧노래를 흥얼거리며 꿈틀거리고 있어요!",
        f"💖 {name}는 지금 당신과 함께라 너무 행복하대요!",
    ]
    random_feeling = random.choice(feelings)

    # 화려한 전광판 스타일 레이아웃 조립
    status_msg = (
        f"📊🔍 [ S T A T U S ] 🔍📊\n\n"
        f"🐾 이름: {name}\n\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"⭐ 레벨: {level} | 경험치: {exp}%\n"
        f"❤️ 남은 체력: {health}%\n"
        f"✨ 경험치: {exp}%\n"
        f"━━━━━━━━━━━━━━━━\n\n"
        f"{random_feeling}"
    )
    image_url = get_malang_image(int(malang["level"]), malang.get("type", "typeA"))
    return status_msg, image_url


# 랭킹 함수
def get_room_rankings_top3(room_id):
    from boto3.dynamodb.conditions import Attr

    response = table.scan(FilterExpression=Attr("room_id").eq(room_id))
    items = response.get("Items", [])

    if not items:
        return "이 방에는 아직 등록된 말랑이가 없어요! 🌱", None

    # 1. 정렬 (레벨 -> 경험치 순)
    sorted_items = sorted(
        items,
        key=lambda x: (int(x.get("level", 1)), int(x.get("exp", 0))),
        reverse=True,
    )
    # 2. 상위 3명만 추출
    top_3 = sorted_items[:3]

    header = ""

    # 3. 랭킹 리스트 텍스트 조립
    rank_list_text = ""
    medals = ["🥇", "🥈", "🥉"]

    for i, user in enumerate(top_3):
        m_name = user.get("malang_name", "말랑이")
        lvl = int(user.get("level", 1))

        # 예시: 🥇 '초코' (Lv.12)
        rank_list_text += f"{medals[i]} '{m_name}' (Lv.{lvl})\n"

    bodys = [
        (
            f"현재 우리 채팅방에서 가장 빛나는\n"
            f"상위 3인의 말랑이 리스트입니다!\n\n"
            f"{rank_list_text.strip()}"
        ),
        (
            f"현재 우리 방에서 가장 정성스럽게\n"
            f"육성된 상위 3인의 말랑이입니다!\n\n"
            f"{rank_list_text.strip()}"
        ),
    ]
    body_msg = random.choice(bodys)

    footer = "✨ 1위의 자리를 노려보세요!"

    # 4. 최종 메시지 조립 (기깔나는 UI 적용)
    final_msg = f"{header}\n\n" f"{body_msg}\n\n" f"━━━━━━━━━━━━━━━━\n" f"{footer}"

    return final_msg, get_system_image("rank_default")
