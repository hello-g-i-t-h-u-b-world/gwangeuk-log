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


# 깨진 글자 지우기
# 한글은 한 글자가 3바이트인데, 터미널에서 백스페이스를 누르면 1바이트만 지워질 때가 있다.
# 그러면 남은 2바이트가 깨진 글자가 되어서 화면에는 � 로 보이고,
# 파이썬은 이걸 \udc80 ~ \udcff 사이의 특수 문자(서로게이트)로 받는다.
# 이게 data 에 들어가면 json 저장이 실패하니까 입력받을 때 미리 지운다.
# (지운 게 있으면 removed 가 True)
def remove_broken_text(text):
    result = ""
    removed = False
    for ch in text:
        code = ord(ch)
        if code >= 0xD800 and code <= 0xDFFF:       # 깨진 바이트
            removed = True
            continue
        if code == 0xFFFD:                          # 이미 � 로 바뀌어서 들어온 경우
            removed = True
            continue
        result = result + ch
    return result, removed


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


# 연도 확인하기 (월별 통계에서 쓴다)
def check_year(text):
    value, error = check_required(text, "연도")
    if value == None:
        return None, error

    try:
        number = int(value)
    except:
        return None, "연도는 숫자만 입력해주세요. (예: 2026)"

    if number < 1900 or number > 2100:
        return None, "연도는 1900 ~ 2100 사이로 입력해주세요. (예: 2026)"
    return number, ""


# 월 확인하기 (월별 통계에서 쓴다)
def check_month(text):
    value, error = check_required(text, "월")
    if value == None:
        return None, error

    try:
        number = int(value)
    except:
        return None, "월은 숫자만 입력해주세요. (예: 8)"

    if number < 1 or number > 12:
        return None, "월은 1 ~ 12 사이로 입력해주세요."
    return number, ""


# 검색 기준 고른 거 확인하기 (FR-06)
def check_search_type(text):
    value, error = check_required(text, "검색 기준")
    if value == None:
        return None, error

    if value == "1" or value == "공연명":
        return "공연명", ""
    if value == "2" or value == "공연장":
        return "공연장", ""
    if value == "3" or value == "캐스팅":
        return "캐스팅", ""

    return None, "검색 기준은 1 ~ 3 사이의 번호로 골라주세요."


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


# ============================================================
# 2차 검증 (설계서 MOD-003 처리 절차 2, 시퀀스 다이어그램 11 ~ 12)
#
# 위에 있는 함수들은 cli.py 가 사용자가 친 글자를 검사하는 1차 검증이고,
# 아래 함수들은 service.py 가 저장하기 직전에 완성된 값을 한 번 더 검사하는 2차 검증이다.
# 필수값이 다 있는지, 서로 안 맞는 값(모순)은 없는지 본다.
# 문제가 없으면 "" 를, 문제가 있으면 오류 메시지를 돌려준다.
# ============================================================

# 금액이 0 이상의 정수인지 확인하기
def is_money(value):
    if type(value) != int:
        return False
    if value < 0:
        return False
    return True


# 공연 2차 검증 (EH-02 : 공연명은 필수)
def check_performance(title):
    value, error = check_required(title, "공연명")
    if value == None:
        return error
    return ""


# 관람 기록 2차 검증 (EH-01, EH-02 + 항목 간 모순)
def check_viewing(date, expense):
    # 1. 관람일 : 필수 + YYYY-MM-DD 형식
    value, error = check_date(date)
    if value == None:
        return error

    # 2. 거래 유형 : 필수 + 셋 중 하나
    if expense["trade_type"] not in TRADE_LIST:
        return "거래 유형은 직접구매 / 양도받음 / 양도함 중 하나여야 합니다."

    # 3. 금액들 : 티켓 정가, 예매 수수료는 필수, 전부 0 이상의 숫자
    if is_money(expense["ticket_price"]) == False:
        return "티켓 정가는 0 이상의 숫자여야 합니다."
    if is_money(expense["booking_fee"]) == False:
        return "예매 수수료는 0 이상의 숫자여야 합니다."
    if is_money(expense["transfer_income"]) == False:
        return "양도 금액은 0 이상의 숫자여야 합니다."

    # 4. 할인율 : 0 ~ 1 사이 (10% 는 0.1)
    rate = expense["discount_rate"]
    if type(rate) != float and type(rate) != int:
        return "할인율이 숫자가 아닙니다."
    if rate < 0 or rate > 1:
        return "할인율은 0 ~ 100% 사이여야 합니다."

    # 5. 쿠폰, MD : 이름이 있어야 하고 금액은 0 이상
    for coupon in expense["coupons"]:
        if coupon["name"].strip() == "":
            return "쿠폰명이 비어 있습니다."
        if is_money(coupon["amount"]) == False:
            return "쿠폰 금액은 0 이상의 숫자여야 합니다."
    for item in expense["md_items"]:
        if item["name"].strip() == "":
            return "MD 이름이 비어 있습니다."
        if is_money(item["amount"]) == False:
            return "MD 금액은 0 이상의 숫자여야 합니다."

    # 6. 항목 간 모순
    # 양도받은 티켓은 양도자한테 준 돈만 쓰니까 할인, 쿠폰, 수수료가 있으면 안 맞는다
    if expense["trade_type"] == "양도받음":
        if rate > 0 or len(expense["coupons"]) > 0 or expense["booking_fee"] > 0:
            return "양도받은 티켓에는 할인, 쿠폰, 예매 수수료를 넣을 수 없습니다."
    # 양도하지 않았는데 양도하고 받은 돈이 있으면 안 맞는다
    if expense["trade_type"] != "양도함" and expense["transfer_income"] > 0:
        return "양도함이 아닌데 양도 금액이 들어가 있습니다."

    return ""
