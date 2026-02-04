import boto3
import os
import random
from dotenv import load_dotenv
from decimal import Decimal
from datetime import datetime
import random

load_dotenv()

# DynamoDB 접속 설정
dynamodb = boto3.resource(
    "dynamodb",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION"),
)

table = dynamodb.Table("MalangUsers")


# 말랑이 가져오기 및 추가
def get_or_create_malang(user_id):
    # 1. 유저가 이미 있는지 확인
    response = table.get_item(Key={"user_id": user_id})
    item = response.get("Item")

    # 2. 없다면 새로 생성 (분양!)
    if not item:
        item = {
            "user_id": user_id,
            "level": 1,
            "exp": 0,
            "health": 100,  # 새로 추가된 체력!
            "max_health": 100,  # 최대 체력 기준
            "name": "성장이 기대되는 말랑이",
        }
        table.put_item(Item=item)
    else:
        # DB에서 가져온 숫자를 안전하게 int로 변환
        item["level"] = int(item["level"])
        item["health"] = int(item["health"])
        item["max_health"] = int(item["max_health"])
        item["exp"] = int(item["exp"])

    return item


# 이미지 매칭 함수
def get_malang_image(level, malang_type="basic"):
    # 1. 레벨에 따른 이미지 번호 결정 (최대 15장 기준)
    # 레벨이 15를 넘어가면 계속 15번 이미지를 보여주도록 제한(clamping)
    img_num = min(level, 15)

    # 2. 깃허브 Raw 이미지 기본 경로
    base_url = "https://raw.githubusercontent.com/MODIFYC/MalangMaker/main/images"

    # 3. 최종 URL 조립 (예: typeA (1).png)
    image_url = f"{base_url}/{malang_type} ({img_num}).png"

    return image_url


# 말랑이 먹이주기
def feed_malang(user_id):
    malang = get_or_create_malang(user_id)
    rand_val = random.random()  # 0.0 ~ 1.0 사이의 랜덤값

    new_health = int(malang["health"])
    new_level = int(malang["level"])
    new_exp = int(malang["exp"])

    # 1. 상황별 랜덤 대사 리스트
    normal_feedback = [
        "✨ (와구와구) 냠냠! 말랑이가 {food_name}을(를) 먹고 꼬리를 살랑살랑 흔들고 있어! 🐾",
        "🍬 말랑말랑! {food_name}은(는) 정말 꿀맛이래! 말랑이의 눈이 반짝반짝 빛나고 있어! 👀✨",
        "🎈 퐁신퐁신~ {food_name}을(를) 먹더니 말랑이의 몸이 더 부풀어 올랐어! 기분 최고! 🌈",
        "🍭 말랑이가 {food_name}을(를) 소중하게 꼭 껴안고 먹고 있어! 너무 행복해 보여! 🥰",
        "🧁 달콤한 {food_name} 냄새가 솔솔~ 말랑이가 기분이 좋아서 노래를 흥얼거려! 🎵",
    ]
    bad_feedback = [
        "🤢 으아앙! 상한 밥이었나봐... 말랑이 얼굴이 파랗게 질려서 부들부들 떨고 있어... 🚑💨",
        "🍄 꾸르륵... 말랑이 배에서 이상한 소리가 나! '말랑... 살려줘...' 라고 하는 것 같아... 😿",
        "⛈️ 콰광! 잘못된 식사였어! 말랑이가 구석에 웅크리고 시무룩해졌어... 미안해 말랑아! 💔",
        "😵 말랑이가 갑자기 핑글핑글 돌더니 털썩 주저앉았어! 배가 많이 아픈가 봐... 🌪️",
        "🧼 퉤퉤! 비누 맛이 나는 밥이었나? 말랑이가 눈물 한 방울을 툭 흘렸어... 💧",
    ]
    legend_feedback = [
        "🏆 [LEGEND] 헉! 말랑이가 전설의 황금 만두를 한입에 꿀꺽! 갑자기 온몸에서 무지개색 광채가 뿜어져 나와! 🌟🦁🔥",
        "👑 웅장한 음악이 들려...! 전설의 만두 파워로 말랑이가 초사이어인(?)이 되었어! 레벨업 가즈아! 🚀💫",
        "🪐 우주의 기운이 말랑이에게! 전설의 만두를 먹은 말랑이가 공중에 붕 떠올라 빛나고 있어! 🌌✨",
    ]

    # 2. 확률별 로직 처리
    # [0.5% 확률] 전설의 만두 (희귀!!)
    if rand_val < 0.005:
        new_level += 1
        new_health = 100
        new_exp = 0
        header = "💎👑 [ L E G E N D ] 👑💎"
        body_msg = random.choice(legend_feedback)
        footer = "🌟 전설의 말랑이가 탄생했습니다!"

    # [15% 확률] 상한 밥 (실패!!)
    elif rand_val < 0.155:
        damage = random.randint(15, 30)
        new_health -= damage
        header = "💀⛈️ [ F A I L ] ⛈️💀"
        body_msg = random.choice(bad_feedback)
        footer = "💊 얼른 신선한 밥을 줘야겠어요..."

    # [그 외] 무난한 밥 (성공!!)
    else:
        normal_foods = [
            {"name": "고소한 콩떡", "heal": 10, "exp": 15},
            {"name": "달콤한 꿀단지", "heal": 20, "exp": 10},
            {"name": "신선한 산딸기", "heal": 15, "exp": 12},
        ]
        food = random.choice(normal_foods)
        new_health += food["heal"]
        new_exp += food["exp"]
        header = "✨ 🎊 [ SUCCESS ] 🎊 ✨"
        body_msg = random.choice(normal_feedback).format(food_name=food["name"])
        footer = "🍀 말랑이가 다음 밥을 기다려요!"

    # 3. 사후 처리 (범위 제한 및 레벨업)
    new_health = max(0, min(100, new_health))
    if new_exp >= 100:
        new_level += 1
        new_exp -= 100
        new_health = 100
        body_msg += "\n\n✨ [LEVEL UP]\n경험치가 꽉 차서 레벨업했어!"

    # 4. 최종 메시지 조립 (여백과 줄바꿈 강조)
    final_msg = (
        f"{header}\n\n"
        f"{body_msg}\n\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"⭐ Lv.{new_level} | {new_exp}%\n"
        f"❤️ 체력: {new_health}%\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"{footer}"
    )

    # 5. DB 업데이트
    table.update_item(
        Key={"user_id": user_id},
        UpdateExpression="set health=:h, exp=:e, #lvl=:l",
        ExpressionAttributeNames={"#lvl": "level"},
        ExpressionAttributeValues={":h": new_health, ":e": new_exp, ":l": new_level},
    )

    return final_msg, new_health


# 말랑이 체력 확인하기
def update_health(user_id, amount):
    # 1. 현재 말랑이 상태 가져오기
    malang = get_or_create_malang(user_id)
    new_health = malang["health"] + amount

    # 2. 체력이 0 이하인지 체크
    if new_health <= 0:
        # [방법 A] 아예 DB에서 유저 데이터를 삭제 (완전 초기화)
        table.delete_item(Key={"user_id": user_id})
        return None  # '터졌음'을 알리는 신호

    # 3. 생존해 있다면 체력 업데이트 (최대 체력은 안 넘게)
    new_health = min(malang["max_health"], new_health)
    table.update_item(
        Key={"user_id": user_id},
        UpdateExpression="set health=:h",
        ExpressionAttributeValues={":h": new_health},
    )
    return new_health


# 스킬로 성장하기
def special_skill(user_id):
    malang = get_or_create_malang(user_id)
    current_hp = int(malang["health"])
    current_exp = int(malang["exp"])
    current_lvl = int(malang["level"])
    name = malang.get("name", "말랑이")

    # 성공 확률은 현재 체력의 80% 정도
    success_rate = current_hp * 0.8
    is_success = random.randint(1, 100) <= success_rate

    # 1. [실패] 말랑이가 버티지 못하고 터짐 💀
    if not is_success:
        table.delete_item(Key={"user_id": user_id})

        header = "🚨🧨 [ CRITICAL ERROR ] 🧨🚨"
        body_msg = (
            f"💥 콰광!!! 에너지가 폭주합니다!\n\n"
            f"{name}가 기술의 반동을 견디지 못하고\n"
            f"공중에서 산산조각나 버렸습니다..."
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
        return None, final_msg

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

    # DB 업데이트
    table.update_item(
        Key={"user_id": user_id},
        UpdateExpression="set health=:h, exp=:e, #lvl=:l",
        ExpressionAttributeNames={"#lvl": "level"},
        ExpressionAttributeValues={":h": new_health, ":e": new_exp, ":l": new_level},
    )

    return {
        "damage": damage,
        "gain_exp": gain_exp,
        "level": new_level,
        "health": new_health,
        "final_msg": final_msg,
    }, None


# 상태 확인하기
def get_malang_status(user_id):
    malang = get_or_create_malang(user_id)

    # DB 값을 int로 안전하게 변환
    level = int(malang["level"])
    health = int(malang["health"])
    exp = int(malang["exp"])
    max_health = int(malang["max_health"])
    name = malang.get("name", "말랑이")

    # 말랑이의 랜덤 기분 대사
    feelings = [
        f"✨ {name}가 당신을 보며 꼬리를 흔들고 있어요!",
        f"💤 {name}가 기분 좋게 낮잠을 자고 싶어 해요.",
        f"👀 {name}가 배고픈 눈으로 당신의 손을 쳐다봅니다.",
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
        f"❤️ 남은 체력: {max_health}%\n"
        f"✨ 경험치: {exp}%\n"
        f"━━━━━━━━━━━━━━━━\n\n"
        f"{random_feeling}"
    )

    return status_msg


# 교감하기
def stroking_malang(user_id):
    malang = get_or_create_malang(user_id)

    # 오늘 날짜 구하기 (YYYY-MM-DD)
    today = datetime.now().strftime("%Y-%m-%d")
    last_date = malang.get("last_stroking_malang", "")

    # 1. 이미 오늘 교감했다면?
    if last_date == today:
        header = "🐾✨ [ R E J E C T ] ✨🐾"
        body_msg = (
            f"말랑이는 이미 충분히 사랑받았어요!\n\n"
            f"지금은 기분 좋게 낮잠을 자고 있네요.\n"
            f"내일 다시 쓰다듬어주세요! 💤"
        )
        footer = "🌙 말랑이가 꿈속에서 당신을 만난대요."

    # 2. 오늘 처음 교감하는 거라면?
    else:
        # 보상 설정 (체력 30 회복, 경험치 20 획득)
        new_health = min(100, int(malang["health"]) + 30)
        new_exp = int(malang["exp"]) + 20
        new_level = int(malang["level"])

        # 레벨업 체크
        if new_exp >= 100:
            new_level += 1
            new_exp -= 100
            new_health = 100

        # DB 업데이트 (오늘 날짜 기록)
        table.update_item(
            Key={"user_id": user_id},
            UpdateExpression="set health=:h, exp=:e, #lvl=:l, last_stroking_malang=:d",
            ExpressionAttributeNames={"#lvl": "level"},
            ExpressionAttributeValues={
                ":h": new_health,
                ":e": new_exp,
                ":l": new_level,
                ":d": today,
            },
        )

        header = "🌕🛏️ [ C O M F O R T ] 🛏️🌕"
        body_msg = (
            f"당신의 따뜻한 손길이 닿았습니다!\n\n"
            f"말랑이가 기분이 좋아져서 몸을 배베 꼬며\n"
            f"당신의 손에 머리를 부비적거려요! 😍"
        )
        footer = "📈 체력 +30 / 경험치 +20 보너스!"

    # 최종 메시지 조립
    final_msg = (
        f"{header}\n\n"
        f"{body_msg}\n\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"⭐ Lv.{malang['level'] if last_date == today else new_level} | {malang["exp"]}%\n"
        f"❤️ 체력: {malang['health'] if last_date == today else new_health}%\n"
        f"━━━━━━━━━━━━━━━━\n\n"
        f"{footer}"
    )

    return final_msg


# 똥치우기
def clean_malang(user_id):
    malang = get_or_create_malang(user_id)
    today = datetime.now().strftime("%Y-%m-%d")

    # DB에서 날짜와 횟수 가져오기 (없으면 초기값)
    last_date = malang.get("last_clean_date", "")
    clean_count = int(malang.get("clean_count", 0))
    name = malang.get("name", "말랑이")

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
            "밤새 말랑이가 엄청난 걸 생산해놨군요!\n\n"
            "코를 막고 구석구석 깨끗이 치웠습니다.\n"
            "말랑이가 부끄러운지 몸을 숨기네요. 🫣"
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
            "말랑이 집에서 빛이 나고 있어요!\n\n"
            "이미 오늘 두 번이나 청소하셨잖아요.\n"
            "내일 다시 똥이 쌓이길 기다려주세요! 💤"
        )
        footer = "🧹 환경 미화원 칭호 획득 대기 중..."

    # 레벨업 체크 및 DB 업데이트 로직 (생략 - 이전과 동일)
    lv_up_msg = ""
    if new_exp >= 100:
        new_level += 1
        new_exp -= 100
        new_health = 100
        lv_up_msg = "\n✨ [LEVEL UP] \n한계를 돌파하여 레벨업했습니다!"
        header = "🔥⚡ [ U L T I M A T E ] ⚡🔥"
        body_msg = (
            f"⚔️ {name}의 필살기 전개!!\n\n"
            f"강력한 일격으로 주변이 진동합니다!\n"
            f"힘을 쏟아부은 {name}가 가쁜 숨을 쉽니다.{lv_up_msg}"
        )
        footer = "💪 다음 기술을 위해 체력을 회복하세요!"

    # 최종 메시지 조립
    final_msg = (
        f"{header}\n\n"
        f"{body_msg}\n\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"⭐ Lv.{new_level} | {new_exp}%\n"
        f"❤️ 체력: {new_health}%\n"
        f"━━━━━━━━━━━━━━━━\n\n"
        f"{footer}"
    )

    # DB 업데이트 (횟수와 날짜 저장)
    table.update_item(
        Key={"user_id": user_id},
        UpdateExpression="set health=:h, exp=:e, last_clean_date=:d, clean_count=:c",
        ExpressionAttributeValues={
            ":h": new_health,
            ":e": new_exp,
            ":d": today,
            ":c": clean_count,
        },
    )

    return final_msg


# 랭킹
def get_room_rankings_top3(room_id):
    # 1. 우리 방(room_id) 데이터만 필터링해서 스캔
    # (SAA 팁: 운영 단계에서는 FilterExpression보다 GSI + Query가 훨씬 효율적!)
    from boto3.dynamodb.conditions import Attr

    response = table.scan(FilterExpression=Attr("room_id").eq(room_id))
    items = response.get("Items", [])

    if not items:
        return "이 방에는 아직 등록된 말랑이가 없어요! 🌱"

    # 2. 레벨 -> 경험치 순으로 정렬 (내림차순)
    sorted_items = sorted(
        items,
        key=lambda x: (int(x.get("level", 1)), int(x.get("exp", 0))),
        reverse=True,
    )

    # 3. 상위 3명만 추출
    top_3 = sorted_items[:3]

    header = "🏆 ─── ✨ [ TOP 3 RANK ] ✨ ─── 🏆"

    # 4. 랭킹 텍스트 조립 (유저 언급 포함)
    rank_list_text = ""
    medals = ["🥇", "🥈", "🥉"]

    for i, user in enumerate(top_3):
        # DB에 저장된 유저 닉네임 또는 말랑이 이름을 가져옴
        nickname = user.get("nickname", "익명의 집사")
        malang_name = user.get("name", "말랑이")
        lvl = user.get("level", 1)

        # 유저를 언급하는 느낌으로 구성
        rank_list_text += f"{medals[i]} {nickname}님 (Lv.{lvl} {malang_name})\n"

    body_msg = (
        f"이 채팅방의 전설적인 집사들!\n"
        f"영광의 상위 3인을 공개합니다.\n\n"
        f"{rank_list_text}"
    )

    footer = "✨ 나머지 분들도 분발해서 3위 안에 드세요!"

    # 확정된 UI 레이아웃 적용
    final_msg = (
        f"{header}\n\n"
        f"{body_msg}\n\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"📍 {room_id[:8]}... 방 랭킹\n"
        f"━━━━━━━━━━━━━━━━\n\n"
        f"{footer}"
    )

    return final_msg
