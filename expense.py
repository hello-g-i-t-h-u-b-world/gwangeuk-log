# ============================================================
# expense.py - 지출 계산하는 파일 (MOD-004) / FR-02
#
# 실제 구매금액 = 정가 - (정가 x 할인율) - 쿠폰 합계 + 예매 수수료
#                 거래 유형이 '양도받음' 이면 지급한 금액을 그대로 쓴다.
# 순지출 = 실제 구매금액 + MD 합계 - 티켓 양도 금액
#
# 예) 170000 - 17000 - (10000 + 3000) + 2000 = 142000원 (설계서 5.1)
#
# 여기서는 화면에 출력하지 않고 계산만 한다.
# ============================================================


# 지출 정보 기본 모양 만들기 (설계서 5.1 데이터 구조)
def make_empty_expense():
    expense = {}
    expense["ticket_price"] = 0
    expense["discount_name"] = ""
    expense["discount_rate"] = 0.0
    expense["coupons"] = []
    expense["booking_fee"] = 0
    expense["booking_site"] = ""
    expense["trade_type"] = "직접구매"
    expense["actual_price"] = 0
    expense["transfer_income"] = 0
    expense["md_items"] = []
    return expense


# '예매수수료 면제 쿠폰' 인지 확인하기 (띄어쓰기는 무시하고 본다)
def is_fee_free_coupon(name):
    name = name.replace(" ", "")
    if "수수료면제" in name:
        return True
    else:
        return False


# 쿠폰 할인 합계 구하기 (쿠폰은 2개 이상 등록할 수 있다)
def get_coupon_total(expense):
    total = 0
    for coupon in expense["coupons"]:
        # 수수료 면제 쿠폰은 금액을 깎아주는 쿠폰이 아니라서 빼고 더한다
        if is_fee_free_coupon(coupon["name"]) == True:
            continue
        total = total + coupon["amount"]
    return total


# 진짜로 더해질 예매 수수료 구하기
def get_booking_fee(expense):
    # 면제 쿠폰이 하나라도 있으면 수수료는 0원이다
    for coupon in expense["coupons"]:
        if is_fee_free_coupon(coupon["name"]) == True:
            return 0
    return expense["booking_fee"]


# MD 금액 합계 구하기 (MD 도 여러 개 등록할 수 있다)
def get_md_total(expense):
    total = 0
    for item in expense["md_items"]:
        total = total + item["amount"]
    return total


# 할인율로 깎이는 금액 구하기 (정가 x 할인율)
def get_discount_price(expense):
    money = expense["ticket_price"] * expense["discount_rate"]
    return int(round(money))


# 실제 구매금액 계산하기. (금액, 안내문구) 로 돌려준다
def calculate_actual_price(expense):
    # 양도받은 티켓은 양도자한테 준 돈이 그대로 실제 구매금액이다
    if expense["trade_type"] == "양도받음":
        return expense["ticket_price"], ""

    price = expense["ticket_price"]
    price = price - get_discount_price(expense)
    price = price - get_coupon_total(expense)
    price = price + get_booking_fee(expense)

    # 쿠폰이 너무 커서 금액이 마이너스가 되면 0원으로 바꾼다
    if price < 0:
        return 0, "할인·쿠폰 금액이 결제 금액보다 커서 실제 구매금액을 0원으로 처리했습니다."

    return price, ""


# 순지출 계산하기
def calculate_net_expense(expense):
    net = expense["actual_price"]
    net = net + get_md_total(expense)
    net = net - expense["transfer_income"]
    return net


# 계산해서 actual_price 칸을 채워넣기 (service.py 가 부른다)
def calculate_expense(expense):
    if expense["trade_type"] == "양도받음":
        # 양도받음은 정가, 할인, 수수료를 안 쓰니까 값이 남아있지 않게 지운다
        expense["discount_name"] = ""
        expense["discount_rate"] = 0.0
        expense["coupons"] = []
        expense["booking_fee"] = 0

    if expense["trade_type"] != "양도함":
        # 양도한 게 아니면 양도 받은 돈도 없다
        expense["transfer_income"] = 0

    price, message = calculate_actual_price(expense)
    expense["actual_price"] = price
    return expense, message
