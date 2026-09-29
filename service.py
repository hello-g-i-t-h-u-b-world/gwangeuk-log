# ============================================================
# service.py - 공연이랑 관람 기록 관리하는 파일 (MOD-003) / FR-01, FR-06
#
# cli.py 에서 입력받은 값으로 메모리에 있는 data 를 고치고,
# 고칠 때마다 repository.py 를 불러서 바로 저장한다.
# 지출 계산이 필요하면 expense.py 한테 시킨다.
# 통계 요청은 statistics.py 한테 넘기고 결과만 cli.py 로 돌려준다.
# (통계는 data 를 안 고치니까 저장은 안 한다)
#
# 데이터를 고치는 순서 (설계서 MOD-003, 시퀀스 다이어그램 10 ~ 18)
#   1. input_utils.py 로 2차 검증 -> 실패하면 data 를 안 건드리고 오류를 돌려준다
#   2. 관람 기록이면 expense.py 로 금액 계산
#   3. 메모리의 data 수정
#   4. repository.py 로 저장
#
# 등록 / 수정 함수는 (결과, 메시지, 저장 성공 여부) 로 돌려준다.
# 결과가 None 이면 검증에 실패한 거고, 그때 메시지가 오류 내용이다.
# 저장에 실패하면 cli.py 가 "저장하지 못했습니다" 라고 알려준다.
# ============================================================

import expense
import input_utils
import repository
import statistics


# P1, P2 ... 처럼 공연 번호 새로 만들기
def make_performance_id(data):
    number = 0
    for performance in data["performances"]:
        num_text = performance["id"][1:]        # P 다음의 숫자만 떼어낸다
        if num_text.isdigit() == False:
            continue
        if int(num_text) > number:
            number = int(num_text)
    return "P" + str(number + 1)


# V1, V2 ... 관람 기록 번호 새로 만들기
# 공연이 달라도 번호가 겹치면 헷갈려서 전체에서 제일 큰 번호를 찾는다
def make_viewing_id(data):
    number = 0
    for performance in data["performances"]:
        for viewing in performance["viewings"]:
            num_text = viewing["id"][1:]
            if num_text.isdigit() == False:
                continue
            if int(num_text) > number:
                number = int(num_text)
    return "V" + str(number + 1)


# 공연 찾기. 없으면 None
def find_performance(data, performance_id):
    for performance in data["performances"]:
        if performance["id"] == performance_id:
            return performance
    return None


# 관람 기록 찾기. 없으면 None
def find_viewing(data, performance_id, viewing_id):
    performance = find_performance(data, performance_id)
    if performance == None:
        return None

    for viewing in performance["viewings"]:
        if viewing["id"] == viewing_id:
            return viewing
    return None


# 공연 등록하기 (FR-01)
# (공연, 메시지, 저장 성공 여부) 로 돌려준다
def add_performance(data, title, type_name, venue):
    # 1. 2차 검증 : 공연명이 비어 있으면 저장하지 않는다
    error = input_utils.check_performance(title)
    if error != "":
        return None, error, False

    performance = {}
    performance["id"] = make_performance_id(data)
    performance["title"] = title
    performance["type"] = type_name
    performance["venue"] = venue
    performance["viewings"] = []

    data["performances"].append(performance)
    saved = repository.save_data(data)      # 등록하자마자 바로 저장
    return performance, "", saved


# 공연 수정하기
# (공연, 메시지, 저장 성공 여부) 로 돌려준다
def update_performance(data, performance_id, title, type_name, venue):
    performance = find_performance(data, performance_id)
    if performance == None:
        return None, "해당 공연을 찾을 수 없습니다.", False

    # 1. 2차 검증 (실패하면 원래 공연 정보는 그대로 둔다)
    error = input_utils.check_performance(title)
    if error != "":
        return None, error, False

    performance["title"] = title
    performance["type"] = type_name
    performance["venue"] = venue

    saved = repository.save_data(data)
    return performance, "", saved


# 공연 삭제하기 (그 공연의 관람 기록도 같이 지워진다)
# 진짜 지울지 물어보는 건 cli.py 가 먼저 한다 (EH-04)
# 저장까지 잘 되면 True
def delete_performance(data, performance_id):
    performance = find_performance(data, performance_id)
    if performance == None:
        return False

    data["performances"].remove(performance)
    saved = repository.save_data(data)
    return saved


# 관람 기록 추가하기 (FR-01, FR-02)
# (관람기록, 안내문구, 저장 성공 여부) 로 돌려준다
def add_viewing(data, performance_id, date, seat, casting, expense_data):
    performance = find_performance(data, performance_id)
    if performance == None:
        return None, "해당 공연을 찾을 수 없습니다.", False

    # 1. 2차 검증 : 필수값이랑 서로 안 맞는 값이 없는지 확인
    error = input_utils.check_viewing(date, expense_data)
    if error != "":
        return None, error, False

    # 2. 금액 계산은 expense.py 가 한다
    expense_data, message = expense.calculate_expense(expense_data)

    viewing = {}
    viewing["id"] = make_viewing_id(data)
    viewing["date"] = date
    viewing["seat"] = seat
    viewing["casting"] = casting
    viewing["expense"] = expense_data

    performance["viewings"].append(viewing)
    saved = repository.save_data(data)
    return viewing, message, saved


# 관람 기록 수정하기
# expense_data 가 None 이면 지출 정보는 안 고치고 그대로 둔다
# (관람기록, 안내문구, 저장 성공 여부) 로 돌려준다
def update_viewing(data, performance_id, viewing_id, date, seat, casting, expense_data):
    viewing = find_viewing(data, performance_id, viewing_id)
    if viewing == None:
        return None, "해당 관람 기록을 찾을 수 없습니다.", False

    # 1. 2차 검증 (지출 정보를 안 고치면 원래 지출 정보로 검사한다)
    check_expense = expense_data
    if check_expense == None:
        check_expense = viewing["expense"]
    error = input_utils.check_viewing(date, check_expense)
    if error != "":
        return None, error, False           # 실패하면 원래 기록은 그대로 둔다

    viewing["date"] = date
    viewing["seat"] = seat
    viewing["casting"] = casting

    message = ""
    if expense_data != None:
        expense_data, message = expense.calculate_expense(expense_data)
        viewing["expense"] = expense_data

    saved = repository.save_data(data)
    return viewing, message, saved


# 관람 기록 삭제하기 (삭제 확인은 cli.py 가 먼저 한다)
# 저장까지 잘 되면 True
def delete_viewing(data, performance_id, viewing_id):
    performance = find_performance(data, performance_id)
    if performance == None:
        return False

    viewing = find_viewing(data, performance_id, viewing_id)
    if viewing == None:
        return False

    performance["viewings"].remove(viewing)
    saved = repository.save_data(data)
    return saved


# 공연 하나의 순지출 합계 구하기 (공연 목록 화면에 보여주려고 쓴다)
def get_performance_total(performance):
    total = 0
    for viewing in performance["viewings"]:
        total = total + expense.calculate_net_expense(viewing["expense"])
    return total


# ============================================================
# 통계 요청 (FR-03 ~ FR-05)
# statistics.py 한테 넘겨서 받은 결과를 그대로 cli.py 로 돌려준다
# ============================================================

# FR-03 월별 지출 통계
def get_monthly_statistics(data, year, month):
    return statistics.monthly_statistics(data, year, month)


# FR-04 공연별 지출 분석
def get_performance_analysis(data, performance_id):
    return statistics.performance_analysis(data, performance_id)


# FR-05 공연별 순위
def get_ranking(data):
    return statistics.ranking(data)


# ============================================================
# 공연 검색 (FR-06)
# ============================================================

# 공연명 / 공연장 / 캐스팅 중에 하나로 검색하기
# 대소문자는 구분하지 않고, 검색어가 들어있기만 하면 찾는다 (부분 일치)
# 결과는 [{"performance": 공연, "viewings": 보여줄 관람기록들}, ...] 이다
def search_performances(data, search_type, keyword):
    keyword = keyword.strip().lower()
    results = []

    for performance in data["performances"]:
        found_viewings = []

        if search_type == "공연명":
            if keyword in performance["title"].lower():
                found_viewings = performance["viewings"]
            else:
                continue

        elif search_type == "공연장":
            if keyword in performance["venue"].lower():
                found_viewings = performance["viewings"]
            else:
                continue

        elif search_type == "캐스팅":
            # 캐스팅은 관람 기록마다 있어서 관람 기록을 하나씩 봐야 한다
            for viewing in performance["viewings"]:
                for name in viewing["casting"]:
                    if keyword in name.lower():
                        found_viewings.append(viewing)
                        break
            if len(found_viewings) == 0:
                continue

        else:
            continue

        result = {}
        result["performance"] = performance
        result["viewings"] = found_viewings
        results.append(result)

    return results


# ============================================================
# 금액 계산 중계
# 설계서 3.1 구성도에서 cli.py 는 service.py 랑 input_utils.py 만 부른다.
# 그래서 화면에 보여줄 금액이 필요하면 cli.py 가 expense.py 를 직접 부르지 않고
# 여기를 거쳐서 받아간다. (계산은 전부 expense.py 가 한다)
# ============================================================

# 빈 지출 정보 만들기
def make_empty_expense():
    return expense.make_empty_expense()


# 저장하기 전에 계산 결과만 미리 보기 ("저장하시겠습니까? (y/n)" 앞에 보여줄 것)
# 원래 지출 정보는 안 바꾸려고 복사해서 계산한다
# (계산된 지출 정보, 안내문구) 로 돌려준다
def preview_expense(expense_data):
    copy_data = dict(expense_data)
    return expense.calculate_expense(copy_data)


# 순지출
def get_net_expense(expense_data):
    return expense.calculate_net_expense(expense_data)


# MD 합계
def get_md_total(expense_data):
    return expense.get_md_total(expense_data)


# 할인율로 깎인 금액
def get_discount_price(expense_data):
    return expense.get_discount_price(expense_data)


# 실제로 더해진 예매 수수료 (면제 쿠폰이 있으면 0)
def get_booking_fee(expense_data):
    return expense.get_booking_fee(expense_data)


# 예매수수료 면제 쿠폰인지
def is_fee_free_coupon(name):
    return expense.is_fee_free_coupon(name)
