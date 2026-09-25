# ============================================================
# cli.py - 화면 보여주고 입력 받는 파일 (MOD-002)
#
# 화면 규칙 (설계서 6.2)
#  1. 메뉴마다 위에 구분선이랑 제목을 띄워서 어디인지 알 수 있게 한다
#  2. 메뉴를 넘어갈 때마다 화면을 지우고 새로 그린다
#  3. 삭제처럼 되돌릴 수 없는 건 (y/n) 으로 한번 더 물어본다
#
# 계산이랑 저장은 여기서 안 하고 service.py 한테 시킨다.
# 이번 1차 구현은 FR-01, FR-02 랑 json 저장까지다.
# 통계(FR-03~05)랑 검색(FR-06)은 2차에 만들 거라서 안내만 띄운다.
# ============================================================

import os
import expense
import input_utils
import service


# 굵은 구분선
def print_line():
    print("======================================================================")


# 얇은 구분선
def print_line2():
    print("----------------------------------------------------------------------")


# 화면 지우기 (앞에 출력한 게 계속 쌓이지 않게)
def clear_screen():
    if os.name == "nt":
        os.system("cls")
    else:
        print("\033[2J\033[H", end="")


# 화면 맨 위에 구분선이랑 제목 띄우기
def print_header(title, sub):
    clear_screen()
    print_line()
    print(" " + title)
    if sub != "":
        print(" " + sub)
    print_line()


# 한글은 화면에서 두 칸을 차지해서 표를 맞추려면 길이를 따로 세야 한다
def get_width(text):
    width = 0
    for ch in text:
        if ord(ch) > 127:
            width = width + 2
        else:
            width = width + 1
    return width


# 글자 뒤에 빈칸을 채워서 칸 맞추기
def fill(text, size):
    text = str(text)
    while get_width(text) > size:               # 너무 길면 뒤를 잘라낸다
        text = text[0:len(text) - 1]
    while get_width(text) < size:
        text = text + " "
    return text


# 글자 앞에 빈칸을 채워서 칸 맞추기 (금액처럼 오른쪽에 붙일 때)
def fill_right(text, size):
    text = str(text)
    while get_width(text) > size:
        text = text[0:len(text) - 1]
    while get_width(text) < size:
        text = " " + text
    return text


# 금액에 천 단위 콤마 찍기
def won(money):
    return format(money, ",") + "원"


# 입력 받기
# '취소' 를 입력하면 None 을 돌려줘서 이전 메뉴로 돌아가게 한다
def get_input(message):
    try:
        text = input(message)
    except:
        # Ctrl + C 같은 걸로 입력이 끊겨도 프로그램이 죽으면 안 되니까 취소로 본다
        print("")
        return None

    if text.strip() == "취소":
        return None
    return text


# 글자 입력 받기
# must 가 True 면 빈 값은 안 되고, old 가 있으면 엔터만 쳤을 때 원래 값을 쓴다
def input_text(message, name, must, old):
    while True:
        if old == None:
            text = get_input(" " + message + ": ")
        else:
            text = get_input(" " + message + " [" + old + "]: ")

        if text == None:
            return None                         # 취소
        if old != None and text.strip() == "":
            return old                          # 엔터만 치면 원래 값 그대로

        if must == False:
            return text.strip()

        value, error = input_utils.check_required(text, name)
        if value != None:
            return value
        print(" ! " + error)


# 숫자 입력 받기 (EH-01)
def input_number(message, name, old):
    while True:
        if old == None:
            text = get_input(" " + message + ": ")
        else:
            text = get_input(" " + message + " [" + won(old) + "]: ")

        if text == None:
            return None
        if old != None and text.strip() == "":
            return old

        value, error = input_utils.check_number(text, name)
        if value != None:
            return value
        print(" ! " + error)


# 날짜 입력 받기 (EH-01)
def input_date(old):
    while True:
        if old == None:
            text = get_input(" 관람일 (YYYY-MM-DD): ")
        else:
            text = get_input(" 관람일 (YYYY-MM-DD) [" + old + "]: ")

        if text == None:
            return None
        if old != None and text.strip() == "":
            return old

        value, error = input_utils.check_date(text)
        if value != None:
            return value
        print(" ! " + error)


# 할인율 입력 받기
def input_rate(old):
    while True:
        if old == None:
            text = get_input(" 할인율(%) (없으면 0): ")
        else:
            text = get_input(" 할인율(%) [" + make_percent_text(old) + "]: ")

        if text == None:
            return None
        if old != None and text.strip() == "":
            return old

        value, error = input_utils.check_rate(text)
        if value != None:
            return value
        print(" ! " + error)


# 0.1 을 "10" 처럼 보기 좋게 바꾸기
def make_percent_text(rate):
    percent = rate * 100
    if percent == int(percent):
        return str(int(percent))
    else:
        return str(round(percent, 2))


# 메뉴 번호 입력 받기
def input_menu(max_number):
    while True:
        text = get_input("\n 메뉴 번호 (0 ~ " + str(max_number) + "): ")
        if text == None:
            return "0"                          # 취소하면 이전 메뉴로 나간다

        text = text.strip()
        if text.isdigit() == True:
            if int(text) <= max_number:
                return text

        print(" ! 0 ~ " + str(max_number) + " 사이의 번호를 입력해주세요.")


# y / n 물어보기 (EH-04)
def ask_yes_no(message):
    while True:
        text = get_input(" " + message + " (y/n): ")
        if text == None:
            return False

        answer, error = input_utils.check_yes_no(text)
        if answer != None:
            return answer
        print(" ! " + error)


# 엔터 칠 때까지 기다리기
def wait_enter():
    get_input("\n [Enter] 계속하기...")


# 수정할 때 원래 값 꺼내오기 (새로 등록하는 거면 None)
def get_old(old, key):
    if old == None:
        return None
    return old[key]


# ============================================================
# 메인 메뉴 (UI-01)
# ============================================================

def start(data):
    while True:
        print_header("관극로그 : 공연 관람 가계부", "메인 메뉴")

        # 지금까지 등록된 개수를 세서 보여준다
        count = 0
        for performance in data["performances"]:
            count = count + len(performance["viewings"])
        print(" 등록된 공연 " + str(len(data["performances"])) + "건 / 관람 기록 " + str(count) + "건")

        print_line2()
        print(" 1. 공연 관리")
        print(" 2. 관람 기록 관리")
        print(" 3. 통계          (2차 구현 예정)")
        print(" 4. 검색          (2차 구현 예정)")
        print(" 0. 종료")
        print_line2()

        menu = input_menu(4)
        if menu == "1":
            performance_menu(data)
        elif menu == "2":
            viewing_menu(data)
        elif menu == "3":
            not_ready("통계", "FR-03~05")
        elif menu == "4":
            not_ready("검색", "FR-06")
        elif menu == "0":
            return


# 아직 안 만든 메뉴 안내 화면
def not_ready(name, code):
    print_header("관극로그 > " + name, "")
    print(" ! " + name + " 기능(" + code + ")은 2차 구현 예정입니다.")
    print("")
    print(" 이번 1차 구현 범위")
    print("  - FR-01 공연 및 관람 기록 관리")
    print("  - FR-02 티켓 및 지출 내역 관리")
    print("  - json 파일 저장")
    wait_enter()


# ============================================================
# 공연 관리 (UI-02 / FR-01)
# ============================================================

# 공연 목록 표로 보여주기. 한 건도 없으면 안내 문구만 띄운다 (EH-03)
def print_performance_list(data):
    if len(data["performances"]) == 0:
        print(" ! 등록된 공연이 없습니다.")
        return False

    print(" " + fill("ID", 5) + fill("공연명", 20) + fill("종류", 9) + fill("공연장", 16) + fill_right("관람", 5) + fill_right("순지출", 12))
    print_line2()

    for performance in data["performances"]:
        type_name = performance["type"]
        if type_name == "":
            type_name = "-"
        venue = performance["venue"]
        if venue == "":
            venue = "-"

        count = len(performance["viewings"])
        total = service.get_performance_total(performance)

        print(" " + fill(performance["id"], 5) + fill(performance["title"], 20) + fill(type_name, 9) + fill(venue, 16) + fill_right(str(count) + "회", 5) + fill_right(won(total), 12))

    return True


# 공연 하나 고르기
def choose_performance(data, work):
    if print_performance_list(data) == False:
        wait_enter()
        return None

    print_line2()
    while True:
        text = get_input(" " + work + "할 공연 ID (예: P1): ")
        if text == None:
            return None

        performance = service.find_performance(data, text.strip().upper())
        if performance != None:
            return performance
        print(" ! 그런 공연이 없습니다. 목록에 있는 ID 를 확인해주세요.")


def performance_menu(data):
    while True:
        print_header("관극로그 > 공연 관리", "FR-01 공연 및 관람 기록 관리")
        print_performance_list(data)
        print_line2()
        print(" 1. 공연 등록")
        print(" 2. 공연 수정")
        print(" 3. 공연 삭제")
        print(" 0. 이전 메뉴")
        print_line2()

        menu = input_menu(3)
        if menu == "1":
            add_performance_screen(data)
        elif menu == "2":
            update_performance_screen(data)
        elif menu == "3":
            delete_performance_screen(data)
        elif menu == "0":
            return


# 공연 등록 화면
def add_performance_screen(data):
    print_header("관극로그 > 공연 관리 > 공연 등록", "")
    print(" ('취소' 라고 입력하면 이전 메뉴로 돌아갑니다)")
    print("")

    title = input_text("공연명", "공연명", True, None)
    if title == None:
        return
    type_name = input_text("공연 종류 (예: 콘서트/뮤지컬)", "공연 종류", False, None)
    if type_name == None:
        return
    venue = input_text("공연장", "공연장", False, None)
    if venue == None:
        return

    performance = service.add_performance(data, title, type_name, venue)

    print_line2()
    print("  " + performance["id"] + " 등록 완료 : " + performance["title"])
    print("  data.json 에 저장했습니다.")
    wait_enter()


# 공연 수정 화면
def update_performance_screen(data):
    print_header("관극로그 > 공연 관리 > 공연 수정", "")
    performance = choose_performance(data, "수정")
    if performance == None:
        return

    print_header("관극로그 > 공연 관리 > 공연 수정", performance["id"] + " " + performance["title"])
    print(" (엔터만 치면 원래 값 그대로 둡니다 / '취소' 라고 입력하면 이전 메뉴)")
    print("")

    title = input_text("공연명", "공연명", True, performance["title"])
    if title == None:
        return
    type_name = input_text("공연 종류", "공연 종류", False, performance["type"])
    if type_name == None:
        return
    venue = input_text("공연장", "공연장", False, performance["venue"])
    if venue == None:
        return

    service.update_performance(data, performance["id"], title, type_name, venue)

    print_line2()
    print("  " + performance["id"] + " 수정 완료 : " + performance["title"])
    wait_enter()


# 공연 삭제 화면
def delete_performance_screen(data):
    print_header("관극로그 > 공연 관리 > 공연 삭제", "")
    performance = choose_performance(data, "삭제")
    if performance == None:
        return

    # EH-04 : 바로 지우지 않고 지울 대상을 한번 더 보여준 다음에 물어본다
    print_header("관극로그 > 공연 관리 > 공연 삭제", "삭제 확인")
    print("  ID       : " + performance["id"])
    print("  공연명   : " + performance["title"])
    print("  공연장   : " + performance["venue"])
    print("  관람 기록 : " + str(len(performance["viewings"])) + "건 (같이 삭제됩니다)")
    print_line2()

    if ask_yes_no("정말 삭제하시겠습니까?") == False:
        print(" ! 삭제를 취소했습니다.")
        wait_enter()
        return

    service.delete_performance(data, performance["id"])

    print_line2()
    print("  " + performance["id"] + " (" + performance["title"] + ") 삭제 완료")
    wait_enter()


# ============================================================
# 관람 기록 관리 (UI-03 / FR-01, FR-02)
# ============================================================

# 캐스팅 리스트를 "GD, 대성, 태양" 처럼 한 줄로 만들기
def make_casting_text(casting):
    text = ""
    for name in casting:
        if text == "":
            text = name
        else:
            text = text + ", " + name
    if text == "":
        text = "-"
    return text


# 관람 기록 목록 표로 보여주기. 없으면 안내 문구만 띄운다 (EH-03)
def print_viewing_list(performance):
    if len(performance["viewings"]) == 0:
        print(" ! 등록된 관람 기록이 없습니다.")
        return False

    print(" " + fill("ID", 5) + fill("관람일", 12) + fill("좌석", 14) + fill("캐스팅", 15) + fill_right("실제구매", 11) + fill_right("순지출", 11))
    print_line2()

    for viewing in performance["viewings"]:
        seat = viewing["seat"]
        if seat == "":
            seat = "-"
        casting = make_casting_text(viewing["casting"])
        actual = viewing["expense"]["actual_price"]
        net = expense.calculate_net_expense(viewing["expense"])

        print(" " + fill(viewing["id"], 5) + fill(viewing["date"], 12) + fill(seat, 14) + fill(casting, 15) + fill_right(won(actual), 11) + fill_right(won(net), 11))

    return True


# 관람 기록 하나 고르기
def choose_viewing(data, performance, work):
    if print_viewing_list(performance) == False:
        wait_enter()
        return None

    print_line2()
    while True:
        text = get_input(" " + work + "할 관람 기록 ID (예: V1): ")
        if text == None:
            return None

        viewing = service.find_viewing(data, performance["id"], text.strip().upper())
        if viewing != None:
            return viewing
        print(" ! 그런 관람 기록이 없습니다. 목록에 있는 ID 를 확인해주세요.")


def viewing_menu(data):
    print_header("관극로그 > 관람 기록 관리", "")
    performance = choose_performance(data, "선택")
    if performance == None:
        return

    while True:
        venue = performance["venue"]
        if venue == "":
            venue = "-"

        print_header("관극로그 > 관람 기록 관리", performance["id"] + " " + performance["title"] + " @ " + venue)
        print_viewing_list(performance)
        print_line2()
        print(" 1. 관람 기록 추가")
        print(" 2. 관람 기록 상세 보기")
        print(" 3. 관람 기록 수정")
        print(" 4. 관람 기록 삭제")
        print(" 0. 이전 메뉴")
        print_line2()

        menu = input_menu(4)
        if menu == "1":
            add_viewing_screen(data, performance)
        elif menu == "2":
            detail_viewing_screen(data, performance)
        elif menu == "3":
            update_viewing_screen(data, performance)
        elif menu == "4":
            delete_viewing_screen(data, performance)
        elif menu == "0":
            return


# 쿠폰 입력 받기 (2개 이상 등록할 수 있다)
def input_coupons(old):
    print("")
    print_line2()
    print(" [쿠폰] 여러 개 등록할 수 있습니다. 쿠폰명을 안 쓰고 엔터를 치면 끝납니다.")
    print("  * '예매수수료 면제 쿠폰' 은 금액을 0 으로 두면 수수료가 면제됩니다.")

    if old != None:
        print(" 지금 등록된 쿠폰")
        if len(old) == 0:
            print("   - 없음")
        for coupon in old:
            print("   - " + coupon["name"] + " : " + won(coupon["amount"]))
        if ask_yes_no("쿠폰을 다시 입력하시겠습니까?") == False:
            return old

    coupons = []
    while True:
        name = get_input(" 쿠폰명 (" + str(len(coupons) + 1) + "번째, 없으면 엔터): ")
        if name == None:
            return None
        name = name.strip()
        if name == "":
            break

        money = input_number("쿠폰 할인 금액", "쿠폰 할인 금액", None)
        if money == None:
            return None

        coupon = {}
        coupon["name"] = name
        coupon["amount"] = money
        coupons.append(coupon)

    return coupons


# MD 항목 입력 받기 (MD 도 여러 개 등록할 수 있다)
def input_md(old):
    print("")
    print_line2()
    print(" [MD] 여러 개 등록할 수 있습니다. 이름을 안 쓰고 엔터를 치면 끝납니다.")

    if old != None:
        print(" 지금 등록된 MD")
        if len(old) == 0:
            print("   - 없음")
        for item in old:
            print("   - " + item["name"] + " : " + won(item["amount"]))
        if ask_yes_no("MD 를 다시 입력하시겠습니까?") == False:
            return old

    md_items = []
    while True:
        name = get_input(" MD 이름 (" + str(len(md_items) + 1) + "번째, 없으면 엔터): ")
        if name == None:
            return None
        name = name.strip()
        if name == "":
            break

        money = input_number("MD 금액", "MD 금액", None)
        if money == None:
            return None

        item = {}
        item["name"] = name
        item["amount"] = money
        md_items.append(item)

    return md_items


# 지출 정보 입력 받기 (FR-02)
# old 가 있으면 수정하는 거고, 없으면 새로 등록하는 거다
def input_expense(old):
    expense_data = expense.make_empty_expense()

    print("")
    print_line2()
    print(" [지출 정보] 거래 유형부터 골라주세요.")
    print("   1. 직접구매")
    print("   2. 양도받음")
    print("   3. 양도함")

    # 거래 유형 고르기
    while True:
        if old == None:
            text = get_input(" 거래 유형: ")
        else:
            text = get_input(" 거래 유형 [" + old["trade_type"] + "]: ")

        if text == None:
            return None
        if old != None and text.strip() == "":
            trade_type = old["trade_type"]
            break

        trade_type, error = input_utils.check_trade_type(text)
        if trade_type != None:
            break
        print(" ! " + error)

    expense_data["trade_type"] = trade_type

    if trade_type == "양도받음":
        # 양도받은 티켓은 정가랑 할인을 안 물어보고 양도자한테 준 돈만 받는다
        print("")
        print(" 양도받은 티켓은 양도자에게 지급한 금액을 실제 구매금액으로 기록합니다.")

        price = input_number("양도자에게 지급한 금액", "지급 금액", get_old(old, "ticket_price"))
        if price == None:
            return None
        expense_data["ticket_price"] = price
        expense_data["booking_fee"] = 0

        site = input_text("예매처 (모르면 엔터)", "예매처", False, get_old(old, "booking_site"))
        if site == None:
            return None
        expense_data["booking_site"] = site
    else:
        price = input_number("티켓 정가", "티켓 정가", get_old(old, "ticket_price"))
        if price == None:
            return None
        expense_data["ticket_price"] = price

        discount_name = input_text("할인명 (없으면 엔터)", "할인명", False, get_old(old, "discount_name"))
        if discount_name == None:
            return None
        expense_data["discount_name"] = discount_name

        rate = input_rate(get_old(old, "discount_rate"))
        if rate == None:
            return None
        expense_data["discount_rate"] = rate

        coupons = input_coupons(get_old(old, "coupons"))
        if coupons == None:
            return None
        expense_data["coupons"] = coupons

        fee = input_number("예매 수수료", "예매 수수료", get_old(old, "booking_fee"))
        if fee == None:
            return None
        expense_data["booking_fee"] = fee

        site = input_text("예매처 (없으면 엔터)", "예매처", False, get_old(old, "booking_site"))
        if site == None:
            return None
        expense_data["booking_site"] = site

    # 양도한 티켓이면 받은 돈을 입력받아서 순지출에서 뺀다
    if trade_type == "양도함":
        money = input_number("티켓 양도 금액 (받은 금액)", "양도 금액", get_old(old, "transfer_income"))
        if money == None:
            return None
        expense_data["transfer_income"] = money

    md_items = input_md(get_old(old, "md_items"))
    if md_items == None:
        return None
    expense_data["md_items"] = md_items

    return expense_data


# 금액 한 줄 출력하기 (이름이랑 금액 자리를 맞춰서 보여준다)
def print_money(name, money, sign):
    print("  " + fill(name, 26) + " " + sign + " " + fill_right(won(money), 12))


# 관람 기록 한 건이랑 계산 과정 보여주기
def print_viewing_detail(viewing):
    ex = viewing["expense"]

    print("  관람일    : " + viewing["date"])
    if viewing["seat"] == "":
        print("  좌석      : -")
    else:
        print("  좌석      : " + viewing["seat"])
    print("  캐스팅    : " + make_casting_text(viewing["casting"]))
    print("  거래 유형 : " + ex["trade_type"])
    if ex["booking_site"] == "":
        print("  예매처    : -")
    else:
        print("  예매처    : " + ex["booking_site"])
    print_line2()

    if ex["trade_type"] == "양도받음":
        print_money("양도자에게 지급한 금액", ex["ticket_price"], " ")
    else:
        print_money("티켓 정가", ex["ticket_price"], " ")

        # 할인
        discount = expense.get_discount_price(ex)
        if discount > 0:
            discount_name = ex["discount_name"]
            if discount_name == "":
                discount_name = "할인"
            print_money("할인 " + discount_name + " (" + make_percent_text(ex["discount_rate"]) + "%)", discount, "-")

        # 쿠폰
        for coupon in ex["coupons"]:
            if expense.is_fee_free_coupon(coupon["name"]) == True:
                print("  " + fill("쿠폰 " + coupon["name"], 26) + "   " + fill_right("수수료 면제", 12))
            else:
                print_money("쿠폰 " + coupon["name"], coupon["amount"], "-")

        # 예매 수수료
        fee = expense.get_booking_fee(ex)
        if fee == 0 and ex["booking_fee"] > 0:
            print_money("예매 수수료 (면제 적용)", fee, "+")
        else:
            print_money("예매 수수료", fee, "+")

    print_line2()
    print_money("실제 구매금액", ex["actual_price"], " ")

    for item in ex["md_items"]:
        print_money("MD " + item["name"], item["amount"], "+")
    if ex["transfer_income"] > 0:
        print_money("티켓 양도 금액", ex["transfer_income"], "-")

    print_line()
    print_money("순지출", expense.calculate_net_expense(ex), " ")


# 관람 기록 추가 화면
def add_viewing_screen(data, performance):
    print_header("관극로그 > 관람 기록 관리 > 관람 기록 추가", performance["id"] + " " + performance["title"])
    print(" ('취소' 라고 입력하면 이전 메뉴로 돌아갑니다)")
    print("")

    date = input_date(None)
    if date == None:
        return
    seat = input_text("좌석 (예: 1층 R열 8번)", "좌석", False, None)
    if seat == None:
        return
    casting_text = input_text("캐스팅 (쉼표로 구분)", "캐스팅", False, None)
    if casting_text == None:
        return
    casting = input_utils.make_casting_list(casting_text)

    expense_data = input_expense(None)
    if expense_data == None:
        return

    viewing, message = service.add_viewing(data, performance["id"], date, seat, casting, expense_data)
    if viewing == None:
        print(" ! 관람 기록을 등록하지 못했습니다.")
        wait_enter()
        return

    print_header("관극로그 > 관람 기록 관리 > 등록 완료", performance["id"] + " " + performance["title"] + " / " + viewing["id"])
    print_viewing_detail(viewing)
    print_line2()
    if message != "":
        print(" ! " + message)
    print("  " + viewing["id"] + " 등록 완료 - data.json 에 저장했습니다.")
    wait_enter()


# 관람 기록 상세 보기 화면
def detail_viewing_screen(data, performance):
    print_header("관극로그 > 관람 기록 관리 > 상세 보기", performance["id"] + " " + performance["title"])
    viewing = choose_viewing(data, performance, "조회")
    if viewing == None:
        return

    print_header("관극로그 > 관람 기록 관리 > 상세 보기", performance["id"] + " " + performance["title"] + " / " + viewing["id"])
    print_viewing_detail(viewing)
    wait_enter()


# 관람 기록 수정 화면
def update_viewing_screen(data, performance):
    print_header("관극로그 > 관람 기록 관리 > 수정", performance["id"] + " " + performance["title"])
    viewing = choose_viewing(data, performance, "수정")
    if viewing == None:
        return

    print_header("관극로그 > 관람 기록 관리 > 수정", performance["id"] + " " + performance["title"] + " / " + viewing["id"])
    print(" (엔터만 치면 원래 값 그대로 둡니다 / '취소' 라고 입력하면 이전 메뉴)")
    print("")

    date = input_date(viewing["date"])
    if date == None:
        return
    seat = input_text("좌석", "좌석", False, viewing["seat"])
    if seat == None:
        return
    casting_text = input_text("캐스팅 (쉼표로 구분)", "캐스팅", False, make_casting_text(viewing["casting"]))
    if casting_text == None:
        return
    if casting_text == "-":                 # 원래 캐스팅이 없었던 경우
        casting_text = ""
    casting = input_utils.make_casting_list(casting_text)

    # 지출 정보는 안 고칠 수도 있으니까 물어본다
    print_line2()
    expense_data = None
    if ask_yes_no("지출 정보도 수정하시겠습니까?") == True:
        expense_data = input_expense(viewing["expense"])
        if expense_data == None:
            return

    viewing, message = service.update_viewing(data, performance["id"], viewing["id"], date, seat, casting, expense_data)

    print_header("관극로그 > 관람 기록 관리 > 수정 완료", performance["id"] + " " + performance["title"] + " / " + viewing["id"])
    print_viewing_detail(viewing)
    print_line2()
    if message != "":
        print(" ! " + message)
    print("  " + viewing["id"] + " 수정 완료 - data.json 에 저장했습니다.")
    wait_enter()


# 관람 기록 삭제 화면
def delete_viewing_screen(data, performance):
    print_header("관극로그 > 관람 기록 관리 > 삭제", performance["id"] + " " + performance["title"])
    viewing = choose_viewing(data, performance, "삭제")
    if viewing == None:
        return

    # EH-04 : 지울 대상을 한번 더 보여주고 물어본다
    print_header("관극로그 > 관람 기록 관리 > 삭제", "삭제 확인")
    print_viewing_detail(viewing)
    print_line2()

    if ask_yes_no("정말 삭제하시겠습니까?") == False:
        print(" ! 삭제를 취소했습니다.")
        wait_enter()
        return

    service.delete_viewing(data, performance["id"], viewing["id"])

    print_line2()
    print("  " + viewing["id"] + " (" + viewing["date"] + ") 삭제 완료")
    wait_enter()
