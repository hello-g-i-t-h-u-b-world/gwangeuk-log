# ============================================================
# statistics.py - 통계랑 순위 계산하는 파일 (MOD-005)
#
# FR-03 월별 지출 통계
# FR-04 공연별 지출 분석
# FR-05 공연별 순위
#
# service.py 가 조회 조건(연월 또는 공연 ID)을 넘겨주면
# data 에서 조건에 맞는 관람 기록만 골라서 합계를 낸다.
# 여기서는 계산만 하고 화면 출력은 cli.py 가 한다.
# 결과는 (결과, 안내문구) 로 돌려주고, 결과가 None 이면 보여줄 게 없는 거다. (EH-03)
#
# 총 티켓 지출 = 총 실제 구매금액 - 총 양도 금액
# 총 순지출   = 총 티켓 지출 + 총 MD 지출
# 회당 평균   = 총 순지출 / 관람 횟수 (관람 횟수가 0 이면 계산 안 함, EH-05)
# ============================================================

import expense


# 관람 기록 여러 개의 합계 구하기
# viewing_list 는 관람 기록(viewing) 들이 들어있는 리스트
def make_summary(viewing_list):
    total_ticket = 0
    total_md = 0
    total_net = 0

    for viewing in viewing_list:
        ex = viewing["expense"]
        # 티켓 지출은 실제 구매금액에서 양도하고 받은 돈을 뺀 것
        total_ticket = total_ticket + ex["actual_price"] - ex["transfer_income"]
        total_md = total_md + expense.get_md_total(ex)
        total_net = total_net + expense.calculate_net_expense(ex)

    summary = {}
    summary["count"] = len(viewing_list)
    summary["ticket"] = total_ticket
    summary["md"] = total_md
    summary["net"] = total_net
    return summary


# FR-03 월별 지출 통계
# 전체 공연의 관람 기록 중에서 그 연월에 본 것만 골라낸다
def monthly_statistics(data, year, month):
    # 관람일이 "2026-08-21" 모양이라서 앞에 "2026-08" 이 같은지 보면 된다
    if month < 10:
        month_text = str(year) + "-0" + str(month)
    else:
        month_text = str(year) + "-" + str(month)

    rows = []               # 화면에 목록으로 보여줄 것 (공연, 관람기록)
    viewing_list = []       # 합계 낼 것
    for performance in data["performances"]:
        for viewing in performance["viewings"]:
            if viewing["date"][0:7] == month_text:
                row = {}
                row["performance"] = performance
                row["viewing"] = viewing
                rows.append(row)
                viewing_list.append(viewing)

    # EH-03 : 그 달에 본 게 하나도 없으면 안내 문구만 돌려준다
    if len(viewing_list) == 0:
        return None, str(year) + "년 " + str(month) + "월의 관람 기록이 없습니다."

    # 관람일 순서대로 보여주려고 정렬한다
    rows.sort(key=get_row_date)

    result = make_summary(viewing_list)
    result["rows"] = rows
    return result, ""


# 정렬할 때 쓰는 함수 (관람일 꺼내기)
def get_row_date(row):
    return row["viewing"]["date"]


# FR-04 공연별 지출 분석
def performance_analysis(data, performance_id):
    performance = None
    for p in data["performances"]:
        if p["id"] == performance_id:
            performance = p
    if performance == None:
        return None, "해당 공연을 찾을 수 없습니다."

    result = make_summary(performance["viewings"])
    result["performance"] = performance

    # EH-05 : 관람 횟수가 0 이면 나누기를 하면 안 된다
    if result["count"] == 0:
        result["average"] = None
        return result, "관람 기록이 없어서 회당 평균 지출을 계산할 수 없습니다."

    result["average"] = round(result["net"] / result["count"])
    return result, ""


# FR-05 공연별 순위
# 공연마다 총 순지출을 구해서 큰 순서대로 줄 세운다
def ranking(data):
    # EH-03 : 공연이 하나도 없으면 안내 문구만 돌려준다
    if len(data["performances"]) == 0:
        return None, "등록된 공연이 없습니다."

    rank_list = []
    for performance in data["performances"]:
        summary = make_summary(performance["viewings"])
        item = {}
        item["id"] = performance["id"]
        item["title"] = performance["title"]
        item["net"] = summary["net"]
        item["count"] = summary["count"]
        rank_list.append(item)

    # 총 순지출이 큰 순서대로 정렬
    rank_list.sort(key=get_net, reverse=True)

    # 순위 번호 붙이기 (금액이 같으면 같은 순위로 한다)
    for i in range(len(rank_list)):
        if i > 0 and rank_list[i]["net"] == rank_list[i - 1]["net"]:
            rank_list[i]["rank"] = rank_list[i - 1]["rank"]
        else:
            rank_list[i]["rank"] = i + 1

    return rank_list, ""


# 정렬할 때 쓰는 함수 (순지출 꺼내기)
def get_net(item):
    return item["net"]
