# ============================================================
# input_utils.py - 입력값 검사하는 파일 (MOD-007)
#
# 숫자, 날짜, 필수 항목이 제대로 들어왔는지 확인한다. (EH-01, EH-02)
# 여기서는 input() 을 하지 않고 검사만 한다.
# 검사 결과는 (값, 오류메시지) 로 돌려주고,
# 값이 None 이면 잘못 입력한 것이라서 cli.py 가 다시 입력을 받는다.
# ============================================================

import re
import datetime

# 거래 유형 (설계서 5.1)
TRADE_LIST = ["직접구매", "양도받음", "양도함"]


# 빈 값인지 확인하기 (EH-02)
def check_required(text, name):
    if text == None:
        return None, name + "은(는) 필수 항목입니다. 다시 입력해주세요."

    text = text.strip()
    if text == "":
        return None, name + "은(는) 필수 항목입니다. 다시 입력해주세요."

    return text, ""


# 숫자가 맞는지 확인하기 (EH-01)
def check_number(text, name):
    value, error = check_required(text, name)
    if value == None:
        return None, error

    # 170,000원 이렇게 입력해도 되게 콤마랑 '원' 은 지운다
    value = value.replace(",", "")
    value = value.replace(" ", "")
    if value.endswith("원") == True:
        value = value[0:len(value) - 1]

    try:
        number = int(value)
    except:
        return None, name + "은(는) 숫자만 입력해주세요. (예: 170000)"

    if number < 0:
        return None, name + "은(는) 0보다 작을 수 없습니다."

    return number, ""


# 할인율 확인하기. 10 을 입력하면 0.1 로 바꿔서 돌려준다
# (설계서 5.1 의 discount_rate 가 0.1 형태라서 이렇게 맞춘다)
def check_rate(text):
    if text == None:
        return 0.0, ""

    text = text.strip()
    if text == "":
        return 0.0, ""          # 아무것도 안 쓰면 할인 없음

    text = text.replace("%", "")
    try:
        percent = float(text)
    except:
        return None, "할인율은(는) 숫자만 입력해주세요. (예: 10)"

    if percent < 0:
        return None, "할인율은(는) 0보다 작을 수 없습니다."
    if percent > 100:
        return None, "할인율은(는) 100%를 넘을 수 없습니다."

    return round(percent / 100, 4), ""


# 날짜가 YYYY-MM-DD 형식인지 확인하기 (EH-01)
def check_date(text):
    value, error = check_required(text, "관람일")
    if value == None:
        return None, error

    # 정규식으로 모양부터 확인한다
    if re.match("^[0-9]{4}-[0-9]{2}-[0-9]{2}$", value) == None:
        return None, "관람일은(는) YYYY-MM-DD 형식으로 입력해주세요. (예: 2026-08-21)"

    year = int(value[0:4])
    month = int(value[5:7])
    day = int(value[8:10])

    if month < 1 or month > 12:
        return None, "월은 1 ~ 12 사이로 입력해주세요."
    if day < 1 or day > 31:
        return None, "일은 1 ~ 31 사이로 입력해주세요."

    # 2월 31일 같이 없는 날짜를 걸러내려고 진짜 날짜로 만들어본다
    try:
        datetime.date(year, month, day)
    except:
        return None, "없는 날짜입니다. 관람일을(를) 다시 확인해주세요."

    return value, ""


# 거래 유형 고른 거 확인하기
def check_trade_type(text):
    value, error = check_required(text, "거래 유형")
    if value == None:
        return None, error

    if value == "1" or value == "직접구매":
        return "직접구매", ""
    if value == "2" or value == "양도받음":
        return "양도받음", ""
    if value == "3" or value == "양도함":
        return "양도함", ""

    return None, "거래 유형은 1 ~ 3 사이의 번호로 골라주세요."


# y / n 확인하기 (EH-04 삭제 확인용)
def check_yes_no(text):
    if text == None:
        return None, "y 또는 n 으로 입력해주세요."

    value = text.strip().lower()
    if value == "":
        return None, "y 또는 n 으로 입력해주세요."

    if value == "y" or value == "yes":
        return True, ""
    if value == "n" or value == "no":
        return False, ""

    return None, "y 또는 n 으로 입력해주세요."


# 캐스팅을 쉼표로 잘라서 리스트로 만들기
def make_casting_list(text):
    casting = []
    if text == None:
        return casting

    for name in text.split(","):
        name = name.strip()
        if name != "":
            casting.append(name)

    return casting
