# ============================================================
# service.py - 공연이랑 관람 기록 관리하는 파일 (MOD-003) / FR-01
#
# cli.py 에서 입력받은 값으로 메모리에 있는 data 를 고치고,
# 고칠 때마다 repository.py 를 불러서 바로 저장한다.
# 지출 계산이 필요하면 expense.py 한테 시킨다.
# ============================================================

import expense
import repository


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
def add_performance(data, title, type_name, venue):
    performance = {}
    performance["id"] = make_performance_id(data)
    performance["title"] = title
    performance["type"] = type_name
    performance["venue"] = venue
    performance["viewings"] = []

    data["performances"].append(performance)
    repository.save_data(data)              # 등록하자마자 바로 저장
    return performance


# 공연 수정하기
def update_performance(data, performance_id, title, type_name, venue):
    performance = find_performance(data, performance_id)
    if performance == None:
        return False

    performance["title"] = title
    performance["type"] = type_name
    performance["venue"] = venue

    repository.save_data(data)
    return True


# 공연 삭제하기 (그 공연의 관람 기록도 같이 지워진다)
# 진짜 지울지 물어보는 건 cli.py 가 먼저 한다 (EH-04)
def delete_performance(data, performance_id):
    performance = find_performance(data, performance_id)
    if performance == None:
        return False

    data["performances"].remove(performance)
    repository.save_data(data)
    return True


# 관람 기록 추가하기 (FR-01, FR-02)
# (관람기록, 안내문구) 로 돌려준다
def add_viewing(data, performance_id, date, seat, casting, expense_data):
    performance = find_performance(data, performance_id)
    if performance == None:
        return None, ""

    # 금액 계산은 expense.py 가 한다
    expense_data, message = expense.calculate_expense(expense_data)

    viewing = {}
    viewing["id"] = make_viewing_id(data)
    viewing["date"] = date
    viewing["seat"] = seat
    viewing["casting"] = casting
    viewing["expense"] = expense_data

    performance["viewings"].append(viewing)
    repository.save_data(data)
    return viewing, message


# 관람 기록 수정하기
# expense_data 가 None 이면 지출 정보는 안 고치고 그대로 둔다
def update_viewing(data, performance_id, viewing_id, date, seat, casting, expense_data):
    viewing = find_viewing(data, performance_id, viewing_id)
    if viewing == None:
        return None, ""

    viewing["date"] = date
    viewing["seat"] = seat
    viewing["casting"] = casting

    message = ""
    if expense_data != None:
        expense_data, message = expense.calculate_expense(expense_data)
        viewing["expense"] = expense_data

    repository.save_data(data)
    return viewing, message


# 관람 기록 삭제하기 (삭제 확인은 cli.py 가 먼저 한다)
def delete_viewing(data, performance_id, viewing_id):
    performance = find_performance(data, performance_id)
    if performance == None:
        return False

    viewing = find_viewing(data, performance_id, viewing_id)
    if viewing == None:
        return False

    performance["viewings"].remove(viewing)
    repository.save_data(data)
    return True


# 공연 하나의 순지출 합계 구하기 (공연 목록 화면에 보여주려고 쓴다)
def get_performance_total(performance):
    total = 0
    for viewing in performance["viewings"]:
        total = total + expense.calculate_net_expense(viewing["expense"])
    return total
