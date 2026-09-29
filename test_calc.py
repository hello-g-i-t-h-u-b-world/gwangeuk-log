# ============================================================
# test_calc.py - 자체 테스트 (설계서 9. 테스트 설계)
#
# 계산이랑 입력 검사가 손으로 계산한 값이랑 맞는지 확인하는 파일이다.
# 1차 : 테스트1, 2, 3, 7, 8
# 2차 : 테스트4, 5 + 순위 정렬, 검색 (설계서 9장의 자체 테스트)
# 수정 : 깨진 글자 입력 / 저장 실패해도 파일이 안 깨지는지 / 표에서 잘린 글자
# 수정 : service.py 2차 검증 / 저장 전 계산 결과 미리 보기
#
# 실행 방법 : python3 test_calc.py
# ============================================================

import os
import expense
import input_utils
import repository
import service
import statistics
import cli

ok_count = 0
fail_count = 0


# 결과가 정답이랑 같은지 확인해서 O / X 를 찍는다
def check(name, result, answer):
    global ok_count
    global fail_count

    if result == answer:
        ok_count = ok_count + 1
        print(" [O] " + name)
    else:
        fail_count = fail_count + 1
        print(" [X] " + name + "  -> 결과 " + str(result) + " / 정답 " + str(answer))


# 테스트용 지출 정보 만들기
def make_expense(price, rate, coupons, fee, trade_type, transfer, md_items):
    ex = expense.make_empty_expense()
    ex["ticket_price"] = price
    ex["discount_rate"] = rate
    ex["coupons"] = coupons
    ex["booking_fee"] = fee
    ex["trade_type"] = trade_type
    ex["transfer_income"] = transfer
    ex["md_items"] = md_items
    return ex


# 테스트2 : 할인율 + 쿠폰 2개 + 예매 수수료가 같이 걸렸을 때
def test2():
    print("")
    print(" [테스트2] 할인율 + 쿠폰 2개 + 예매 수수료")

    coupons = [{"name": "정부지원 만원쿠폰", "amount": 10000},
               {"name": "네이버 쿠폰", "amount": 3000}]
    md_items = [{"name": "포스터", "amount": 15000}]
    ex = make_expense(170000, 0.1, coupons, 2000, "직접구매", 0, md_items)
    ex, message = expense.calculate_expense(ex)

    # 170000 - 17000 - 13000 + 2000 = 142000
    check("실제 구매금액 142,000원", ex["actual_price"], 142000)
    # 142000 + 15000 = 157000
    check("순지출 157,000원", expense.calculate_net_expense(ex), 157000)

    # 예매수수료 면제 쿠폰이 있으면 수수료가 0원이 된다
    coupons2 = [{"name": "예매수수료 면제 쿠폰", "amount": 0}]
    ex2 = make_expense(100000, 0.0, coupons2, 2000, "직접구매", 0, [])
    ex2, message2 = expense.calculate_expense(ex2)
    check("수수료 면제 쿠폰 적용", ex2["actual_price"], 100000)

    # 쿠폰이 정가보다 크면 0원으로 처리한다
    coupons3 = [{"name": "큰 쿠폰", "amount": 50000}]
    ex3 = make_expense(10000, 0.0, coupons3, 1000, "직접구매", 0, [])
    ex3, message3 = expense.calculate_expense(ex3)
    check("마이너스면 0원 처리", ex3["actual_price"], 0)
    check("0원 처리하면 안내 문구가 나온다", message3 != "", True)


# 테스트3 : 거래 유형이 양도일 때
def test3():
    print("")
    print(" [테스트3] 양도받음 / 양도함")

    # 양도받음은 할인이나 쿠폰이 들어있어도 무시하고 지급액을 그대로 쓴다
    coupons = [{"name": "쿠폰", "amount": 10000}]
    ex = make_expense(90000, 0.5, coupons, 2000, "양도받음", 0, [])
    ex, message = expense.calculate_expense(ex)
    check("양도받음 실제 구매금액 90,000원", ex["actual_price"], 90000)
    check("양도받음은 할인율이 지워진다", ex["discount_rate"], 0.0)
    check("양도받음은 쿠폰이 지워진다", len(ex["coupons"]), 0)

    # 양도함은 순지출에서 양도 금액을 뺀다
    md_items = [{"name": "응원봉", "amount": 30000}]
    ex2 = make_expense(150000, 0.0, [], 2000, "양도함", 140000, md_items)
    ex2, message2 = expense.calculate_expense(ex2)
    check("양도함 실제 구매금액 152,000원", ex2["actual_price"], 152000)
    # 152000 + 30000 - 140000 = 42000
    check("양도함 순지출 42,000원", expense.calculate_net_expense(ex2), 42000)


# 테스트7 : 금액 칸에 문자나 음수를 넣었을 때 (EH-01, EH-02)
def test7():
    print("")
    print(" [테스트7] 잘못된 입력 걸러내기")

    value, error = input_utils.check_number("십만원", "티켓 정가")
    check("문자를 넣으면 오류", value, None)

    value, error = input_utils.check_number("-5000", "티켓 정가")
    check("음수를 넣으면 오류", value, None)

    value, error = input_utils.check_number("170,000원", "티켓 정가")
    check("콤마를 넣어도 읽는다", value, 170000)

    value, error = input_utils.check_required("   ", "공연명")
    check("필수 항목이 비면 오류", value, None)

    value, error = input_utils.check_date("2026/08/21")
    check("날짜 형식이 틀리면 오류", value, None)

    value, error = input_utils.check_date("2026-02-31")
    check("없는 날짜면 오류", value, None)

    value, error = input_utils.check_date("2026-08-21")
    check("날짜가 맞으면 통과", value, "2026-08-21")

    value, error = input_utils.check_rate("10")
    check("할인율 10%는 0.1 로 바뀐다", value, 0.1)

    value, error = input_utils.check_rate("120")
    check("할인율이 100%를 넘으면 오류", value, None)


# 테스트1, 테스트8 : 등록 / 수정 / 삭제랑 껐다 켰을 때 데이터가 남아있는지
def test1_and_8():
    print("")
    print(" [테스트1, 테스트8] 등록/수정/삭제 + 저장 후 다시 불러오기")

    # 진짜 data.json 을 건드리면 안 되니까 테스트용 파일로 바꿔서 한다
    repository.DATA_FILE = "test_data.json"
    if os.path.exists("test_data.json") == True:
        os.remove("test_data.json")

    data, status = repository.load_data()
    check("파일이 없으면 새로 만든다", status, "새파일")

    performance, message, saved = service.add_performance(data, "XX : COSMOS", "콘서트", "고양종합운동장")
    check("공연 번호는 P1", performance["id"], "P1")
    check("공연 등록하면 저장 성공", saved, True)

    # 같은 공연에 관람 기록 3개 등록하기
    day_list = ["2026-08-01", "2026-08-11", "2026-08-21"]
    for day in day_list:
        ex = make_expense(100000, 0.0, [], 2000, "직접구매", 0, [])
        service.add_viewing(data, "P1", day, "A석", [], ex)
    check("관람 기록 3건 등록", len(data["performances"][0]["viewings"]), 3)

    # 하나만 수정하기
    service.update_viewing(data, "P1", "V2", "2026-08-11", "B석", [], None)
    check("V2 좌석만 수정됨", service.find_viewing(data, "P1", "V2")["seat"], "B석")
    check("V1 은 그대로", service.find_viewing(data, "P1", "V1")["seat"], "A석")

    # 하나만 삭제하기
    service.delete_viewing(data, "P1", "V2")
    check("V2 삭제됨", service.find_viewing(data, "P1", "V2"), None)
    check("2건 남음", len(data["performances"][0]["viewings"]), 2)

    # 프로그램을 껐다 켠 것처럼 파일에서 다시 불러오기
    data2, status2 = repository.load_data()
    check("다시 불러오기 성공", status2, "정상")
    check("공연이 그대로 있다", len(data2["performances"]), 1)
    check("관람 기록도 그대로 있다", len(data2["performances"][0]["viewings"]), 2)
    check("금액도 그대로다", data2["performances"][0]["viewings"][0]["expense"]["actual_price"], 102000)

    # 파일이 깨졌을 때 오류로 알려주는지 확인
    f = open("test_data.json", "w", encoding="utf-8")
    f.write("{ 이건 깨진 파일 ")
    f.close()
    data3, status3 = repository.load_data()
    check("깨진 파일은 오류로 알려준다", status3, "오류")

    # 테스트용 파일 정리하기
    if os.path.exists("test_data.json") == True:
        os.remove("test_data.json")
    repository.DATA_FILE = "data.json"


# 2차 테스트에서 같이 쓸 데이터 만들기 (파일 저장은 안 한다)
# P1 : 8월 2번 + 9월 1번 / P2 : 8월 1번 (양도함) / P3 : 관람 기록 없음
def make_test_data():
    data = {"performances": []}

    p1 = {"id": "P1", "title": "XX : COSMOS", "type": "콘서트", "venue": "고양종합운동장", "viewings": []}
    p2 = {"id": "P2", "title": "Les Miserables", "type": "뮤지컬", "venue": "블루스퀘어", "viewings": []}
    p3 = {"id": "P3", "title": "햄릿", "type": "연극", "venue": "예술의전당", "viewings": []}

    # V1 : 142,000 + MD 15,000 = 157,000
    ex1 = make_expense(170000, 0.1, [{"name": "쿠폰A", "amount": 10000}, {"name": "쿠폰B", "amount": 3000}],
                       2000, "직접구매", 0, [{"name": "포스터", "amount": 15000}])
    ex1, m = expense.calculate_expense(ex1)
    p1["viewings"].append({"id": "V1", "date": "2026-08-21", "seat": "1층", "casting": ["GD", "대성"], "expense": ex1})

    # V2 : 양도받음 120,000
    ex2 = make_expense(120000, 0.0, [], 0, "양도받음", 0, [])
    ex2, m = expense.calculate_expense(ex2)
    p1["viewings"].append({"id": "V2", "date": "2026-08-22", "seat": "2층", "casting": ["태양"], "expense": ex2})

    # V3 : 9월 100,000 + 2,000 = 102,000
    ex3 = make_expense(100000, 0.0, [], 2000, "직접구매", 0, [])
    ex3, m = expense.calculate_expense(ex3)
    p1["viewings"].append({"id": "V3", "date": "2026-09-01", "seat": "3층", "casting": ["GD"], "expense": ex3})

    # V4 : 양도함 152,000 + MD 30,000 - 양도 140,000 = 42,000
    ex4 = make_expense(150000, 0.0, [], 2000, "양도함", 140000, [{"name": "응원봉", "amount": 30000}])
    ex4, m = expense.calculate_expense(ex4)
    p2["viewings"].append({"id": "V4", "date": "2026-08-30", "seat": "A석", "casting": ["Jean Valjean"], "expense": ex4})

    data["performances"].append(p1)
    data["performances"].append(p2)
    data["performances"].append(p3)
    return data


# 테스트4 : 월별 통계 + 관람 기록이 없는 달을 조회했을 때 (FR-03, EH-03)
def test4():
    print("")
    print(" [테스트4] 월별 지출 통계")

    data = make_test_data()
    result, message = statistics.monthly_statistics(data, 2026, 8)

    # 8월 : V1, V2, V4
    check("8월 관람 횟수 3회", result["count"], 3)
    # 티켓 지출 = 142000 + 120000 + (152000 - 140000) = 274000
    check("8월 총 티켓 지출 274,000원", result["ticket"], 274000)
    check("8월 총 MD 지출 45,000원", result["md"], 45000)
    # 순지출 = 157000 + 120000 + 42000 = 319000
    check("8월 총 순지출 319,000원", result["net"], 319000)
    check("티켓 지출 + MD 지출 = 순지출", result["ticket"] + result["md"], result["net"])
    check("관람일 순서로 정렬", result["rows"][0]["viewing"]["id"], "V1")

    result, message = statistics.monthly_statistics(data, 2026, 9)
    check("9월 관람 횟수 1회", result["count"], 1)

    # 기록이 없는 달은 에러 없이 안내 문구만 돌려준다
    result, message = statistics.monthly_statistics(data, 2026, 3)
    check("기록 없는 달은 결과 없음", result, None)
    check("기록 없는 달 안내 문구", message, "2026년 3월의 관람 기록이 없습니다.")


# 테스트5 : 공연별 분석 + 관람 기록이 없는 공연의 평균 (FR-04, EH-05)
def test5():
    print("")
    print(" [테스트5] 공연별 지출 분석")

    data = make_test_data()
    result, message = statistics.performance_analysis(data, "P1")
    check("P1 관람 횟수 3회", result["count"], 3)
    # 157000 + 120000 + 102000 = 379000
    check("P1 총 순지출 379,000원", result["net"], 379000)
    check("P1 총 MD 지출 15,000원", result["md"], 15000)
    # 379000 / 3 = 126333.33 -> 126333
    check("P1 회당 평균 126,333원", result["average"], 126333)

    # 관람 기록이 없는 공연 : 0 으로 나누면 안 된다
    result, message = statistics.performance_analysis(data, "P3")
    check("P3 관람 횟수 0회", result["count"], 0)
    check("P3 평균은 계산 안 함", result["average"], None)
    check("P3 안내 문구가 나온다", message != "", True)

    result, message = statistics.performance_analysis(data, "P99")
    check("없는 공연은 결과 없음", result, None)


# 순위 정렬 확인 (FR-05)
def test_ranking():
    print("")
    print(" [순위] 공연별 순위")

    data = make_test_data()
    rank_list, message = statistics.ranking(data)
    # P1 379000 > P2 42000 / P3 은 관람 기록이 없어서 빠진다
    check("순위에 들어간 공연은 2개", len(rank_list), 2)
    check("1위는 P1", rank_list[0]["id"], "P1")
    check("2위는 P2", rank_list[1]["id"], "P2")
    check("1위 총 순지출 379,000원", rank_list[0]["net"], 379000)
    check("1위 관람 횟수 3회", rank_list[0]["count"], 3)
    check("순위 번호", rank_list[1]["rank"], 2)

    # 관람 기록이 없는 P3 는 순위에 없어야 한다
    found_p3 = False
    for item in rank_list:
        if item["id"] == "P3":
            found_p3 = True
    check("관람 기록 없는 P3 는 순위에서 빠짐", found_p3, False)

    # 금액이 같으면 같은 순위
    ex_a = make_expense(50000, 0.0, [], 0, "직접구매", 0, [])
    ex_a, m = expense.calculate_expense(ex_a)
    ex_b = make_expense(50000, 0.0, [], 0, "직접구매", 0, [])
    ex_b, m = expense.calculate_expense(ex_b)
    same = {"performances": [
        {"id": "P1", "title": "A", "type": "", "venue": "", "viewings": [
            {"id": "V1", "date": "2026-08-01", "seat": "", "casting": [], "expense": ex_a}]},
        {"id": "P2", "title": "B", "type": "", "venue": "", "viewings": [
            {"id": "V2", "date": "2026-08-02", "seat": "", "casting": [], "expense": ex_b}]}]}
    rank_list, message = statistics.ranking(same)
    check("금액이 같으면 같은 순위", rank_list[1]["rank"], 1)

    # 공연은 있는데 관람 기록이 하나도 없으면 안내 문구
    no_viewing = {"performances": [
        {"id": "P1", "title": "A", "type": "", "venue": "", "viewings": []}]}
    rank_list, message = statistics.ranking(no_viewing)
    check("관람 기록이 없으면 결과 없음", rank_list, None)
    check("관람 기록이 없으면 안내 문구", message, "관람 기록이 없어서 순위를 매길 수 없습니다.")

    rank_list, message = statistics.ranking({"performances": []})
    check("공연이 없으면 안내 문구", message, "등록된 공연이 없습니다.")

# 검색 확인 (FR-06)
def test_search():
    print("")
    print(" [검색] 공연 검색 및 필터링")

    data = make_test_data()

    results = service.search_performances(data, "공연명", "cosmos")
    check("공연명 소문자로 검색해도 찾는다", len(results), 1)
    check("찾은 공연은 P1", results[0]["performance"]["id"], "P1")
    check("공연명 검색은 관람 기록을 다 보여준다", len(results[0]["viewings"]), 3)

    results = service.search_performances(data, "공연명", "MISER")
    check("대문자 부분 검색", results[0]["performance"]["id"], "P2")

    results = service.search_performances(data, "공연장", "블루")
    check("공연장 부분 검색", results[0]["performance"]["id"], "P2")

    results = service.search_performances(data, "캐스팅", "gd")
    check("캐스팅 검색은 공연 1건", len(results), 1)
    check("캐스팅이 맞는 관람 기록만 보여준다", len(results[0]["viewings"]), 2)

    results = service.search_performances(data, "캐스팅", "valjean")
    check("캐스팅 영어 이름 대소문자 무시", results[0]["performance"]["id"], "P2")

    results = service.search_performances(data, "공연명", "없는공연")
    check("검색 결과가 없으면 빈 리스트", len(results), 0)

    value, error = input_utils.check_year("이천")
    check("연도에 문자를 넣으면 오류", value, None)
    value, error = input_utils.check_month("13")
    check("13월은 오류", value, None)


# 깨진 글자랑 저장 실패 확인
# 한글을 백스페이스로 지우다가 남은 바이트 때문에 data.json 이 깨졌던 문제
def test_broken_text():
    print("")
    print(" [깨진 글자] 입력 걸러내기 + 저장 실패해도 파일이 안 깨지는지")

    # '가' 는 EA B0 80 인데 백스페이스로 80 만 지워지면 EA B0 이 남는다
    # 파이썬은 이걸 \udcea \udcb0 으로 받는다
    text, removed = input_utils.remove_broken_text("2\udcea\udcb0층")
    check("깨진 바이트를 지운다", text, "2층")
    check("지운 게 있으면 True", removed, True)

    text, removed = input_utils.remove_broken_text("\ufffdNOL")
    check("� 문자도 지운다", text, "NOL")

    text, removed = input_utils.remove_broken_text("1층 R열 8번")
    check("정상 입력은 그대로", text, "1층 R열 8번")
    check("정상 입력은 False", removed, False)

    # 저장이 실패해도 원래 data.json 은 그대로 있어야 한다
    repository.DATA_FILE = "test_data.json"
    if os.path.exists("test_data.json") == True:
        os.remove("test_data.json")

    data, status = repository.load_data()
    performance, message, saved = service.add_performance(data, "정상 공연", "콘서트", "공연장")
    check("정상 공연은 저장 성공", saved, True)

    # 깨진 글자가 섞인 공연을 억지로 넣어서 저장 실패를 만든다
    performance, message, saved = service.add_performance(data, "깨진\udcea공연", "콘서트", "공연장")
    check("깨진 글자가 있으면 저장 실패를 알려준다", saved, False)

    data2, status2 = repository.load_data()
    check("저장 실패해도 파일은 안 깨진다", status2, "정상")
    check("원래 들어있던 공연은 그대로", len(data2["performances"]), 1)
    check("원래 공연 이름도 그대로", data2["performances"][0]["title"], "정상 공연")

    if os.path.exists("test_data.json") == True:
        os.remove("test_data.json")
    repository.DATA_FILE = "data.json"


# 표에서 칸보다 긴 글자가 잘릴 때 ".." 이 붙는지 확인
def test_cut_text():
    print("")
    print(" [표 칸 맞추기] 잘린 글자에 .. 붙이기")

    check("캐스팅 3명이 15칸을 넘으면 .. 붙임", cli.fill("태양, 지디, 대성", 15), "태양, 지디..   ")
    check("잘려도 칸 폭은 그대로 15", cli.get_width(cli.fill("태양, 지디, 대성", 15)), 15)
    check("칸 안에 들어가면 안 자름", cli.fill("태양, 지디, 대성", 20), "태양, 지디, 대성    ")
    check("짧은 글자는 그대로", cli.fill("바운디", 8), "바운디  ")
    check("금액 칸도 폭 유지", cli.get_width(cli.fill_right("1,234,567,890원", 11)), 11)


# service.py 2차 검증 확인 (설계서 MOD-003, 시퀀스 다이어그램 11 ~ 12)
# 검증에 실패하면 data 를 안 건드리고 저장도 안 해야 한다
def test_second_check():
    print("")
    print(" [2차 검증] service.py 가 저장 직전에 다시 검사하는지")

    repository.DATA_FILE = "test_data.json"
    if os.path.exists("test_data.json") == True:
        os.remove("test_data.json")
    data, status = repository.load_data()

    performance, message, saved = service.add_performance(data, "   ", "콘서트", "공연장")
    check("공연명이 비면 등록 안 함", performance, None)
    check("공연명 오류 메시지", message, "공연명은(는) 필수 항목입니다. 다시 입력해주세요.")
    check("공연 개수 그대로 0", len(data["performances"]), 0)

    performance, message, saved = service.add_performance(data, "정상 공연", "", "")
    result, message, saved = service.update_performance(data, "P1", "", "", "")
    check("공연 수정도 공연명이 비면 안 함", result, None)
    check("수정 실패하면 원래 공연명 그대로", data["performances"][0]["title"], "정상 공연")

    good = make_expense(100000, 0.0, [], 2000, "직접구매", 0, [])
    viewing, message, saved = service.add_viewing(data, "P1", "2026/08/21", "", [], good)
    check("관람일 형식이 틀리면 등록 안 함", viewing, None)

    bad = make_expense(-100, 0.0, [], 2000, "직접구매", 0, [])
    viewing, message, saved = service.add_viewing(data, "P1", "2026-08-21", "", [], bad)
    check("정가가 음수면 등록 안 함", viewing, None)

    bad = make_expense(100000, 0.0, [], 2000, "양도받음", 0, [])
    viewing, message, saved = service.add_viewing(data, "P1", "2026-08-21", "", [], bad)
    check("양도받음인데 수수료가 있으면 모순이라 등록 안 함", viewing, None)

    bad = make_expense(100000, 0.0, [], 2000, "직접구매", 5000, [])
    viewing, message, saved = service.add_viewing(data, "P1", "2026-08-21", "", [], bad)
    check("양도함이 아닌데 양도 금액이 있으면 등록 안 함", viewing, None)

    bad = make_expense(100000, 0.0, [], 2000, "없는유형", 0, [])
    viewing, message, saved = service.add_viewing(data, "P1", "2026-08-21", "", [], bad)
    check("거래 유형이 이상하면 등록 안 함", viewing, None)
    check("검증 실패한 건 하나도 안 들어감", len(data["performances"][0]["viewings"]), 0)

    viewing, message, saved = service.add_viewing(data, "P1", "2026-08-21", "", [], good)
    check("정상 값은 등록됨", viewing["id"], "V1")
    result, message, saved = service.update_viewing(data, "P1", "V1", "2026-13-01", "B석", [], None)
    check("관람 기록 수정도 날짜가 틀리면 안 함", result, None)
    check("수정 실패하면 원래 좌석 그대로", data["performances"][0]["viewings"][0]["seat"], "")

    # 파일에도 검증 실패한 건 안 들어갔는지
    data2, status2 = repository.load_data()
    check("파일에도 공연 1건, 관람 1건만", len(data2["performances"][0]["viewings"]), 1)

    if os.path.exists("test_data.json") == True:
        os.remove("test_data.json")
    repository.DATA_FILE = "data.json"


# 저장 전에 계산 결과 미리 보기 ("저장하시겠습니까? (y/n)" 앞 화면)
def test_preview():
    print("")
    print(" [미리 보기] 저장 전에 계산 결과 보여주기")

    coupons = [{"name": "정부지원 만원쿠폰", "amount": 10000}, {"name": "네이버 쿠폰", "amount": 3000}]
    ex = make_expense(170000, 0.1, coupons, 2000, "직접구매", 0, [{"name": "포스터", "amount": 15000}])
    preview, message = service.preview_expense(ex)
    check("미리 보기 실제 구매금액 142,000원", preview["actual_price"], 142000)
    check("미리 보기 순지출 157,000원", service.get_net_expense(preview), 157000)
    check("미리 보기는 원래 값을 안 바꾼다", ex["actual_price"], 0)


print("======================================================================")
print(" 관극로그 자체 테스트")
print("======================================================================")

test2()
test3()
test7()
test1_and_8()
test4()
test5()
test_ranking()
test_search()
test_broken_text()
test_cut_text()
test_second_check()
test_preview()

print("")
print("======================================================================")
print(" 성공 " + str(ok_count) + "개 / 실패 " + str(fail_count) + "개")
print("======================================================================")
