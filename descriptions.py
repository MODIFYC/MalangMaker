# 말랑이의 모든 텍스트 데이터를 관리하는 딕셔너리
MALANG_CONFIG = {
    "typeA": {
        "status": {
            # 레벨 구간별 설정
            "levels": [
                {
                    "max_lvl": 2,
                    "title": "[빙하의 알] ❄️",
                    "desc": "맑고 투명한 얼음 조각 같습니다. 차가운 한기가 기분 좋게 느껴져요.",
                },
                {
                    "max_lvl": 4,
                    "title": "[꼬마 서리] ✨",
                    "desc": "작은 손발이 돋아났어요! 스스로 통통 튀어 다니며 성에를 뿌립니다.",
                },
                {
                    "max_lvl": 7,
                    "title": "[수정 가디언] 💎",
                    "desc": "단단한 뿔이 솟아났습니다. 몸 안에서 신비로운 푸른 빛이 자라납니다.",
                },
                {
                    "max_lvl": 10,
                    "title": "[빙룡의 후예] 🐉",
                    "desc": "거대한 수정 날개가 펼쳐졌습니다. 위엄 있는 빙룡의 모습이 보입니다.",
                },
                {
                    "max_lvl": 14,
                    "title": "[고대의 환수] 🌀",
                    "desc": "날개가 날카로운 얼음 깃털로 변했습니다. 주변의 공기를 얼리는 기세입니다.",
                },
                {
                    "max_lvl": 15,
                    "title": "[영원한 빙룡왕] 👑",
                    "desc": "전설의 왕관을 쓴 빙룡의 왕입니다. 가슴의 코어가 생명력을 뿜어냅니다.",
                },
            ],
            # 사망 시 설정
            "dead": {
                "title": "💀 [부서진 결정]",
                "desc": "말랑이가 에너지를 버티지 못하고 흩어졌습니다... 차가운 묘비만이 자리를 지킵니다.",
            },
        }
    }
    # 여기에 typeB, typeC 등을 동일한 구조로 추가 가능
}


def get_malang_data(malang_type, level, is_dead=False):
    """지정한 타입과 레벨에 맞는 title과 desc를 반환하는 함수"""
    # 1. 해당 타입의 status 데이터 가져오기 (기본값 typeA)
    type_conf = MALANG_CONFIG.get(malang_type, MALANG_CONFIG["typeA"])["status"]

    # 2. 사망 상태 처리
    if is_dead:
        return type_conf["dead"]["title"], type_conf["dead"]["desc"]

    # 3. 레벨 구간 매칭
    for stage in type_conf["levels"]:
        if level <= stage["max_lvl"]:
            return stage["title"], stage["desc"]

    # 예외 상황(만렙 이상 등)은 마지막 단계 반환
    return type_conf["levels"][-1]["title"], type_conf["levels"][-1]["desc"]
