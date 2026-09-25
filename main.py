# ============================================================
# main.py - 프로그램 시작하는 파일 (MOD-001)
# 관극로그 : 공연 관람 가계부
#
# 실행 방법 : python3 main.py
#
# 1. data.json 을 불러온다 (켤 때 한 번만)
# 2. cli.py 의 메인 메뉴로 넘어간다
# 3. 사용자가 0번을 고르면 끝낸다
# ============================================================

import cli
import repository


def main():
    # 1. 데이터 불러오기
    data, status = repository.load_data()

    if status == "새파일":
        cli.print_header("관극로그 : 공연 관람 가계부", "시작")
        print(" ! 저장된 데이터가 없어서 새 data.json 파일을 만들었습니다.")
        cli.wait_enter()

    if status == "오류":
        # 파일이 깨져서 못 읽는 경우 (설계서 MOD-006)
        cli.print_header("관극로그 : 공연 관람 가계부", "데이터 불러오기 실패")
        print(" ! data.json 파일을 읽을 수 없습니다. (파일이 깨진 것 같습니다)")
        print("")
        print(" 원래 파일은 지우지 않고 data_backup.json 으로 옮겨둔 다음에")
        print(" 빈 데이터로 새로 시작할 수 있습니다.")
        cli.print_line2()

        if cli.ask_yes_no("새 데이터 파일로 다시 시작하시겠습니까?") == False:
            print("")
            print(" 프로그램을 종료합니다. data.json 파일을 확인한 다음에 다시 실행해주세요.")
            return

        data = repository.start_new_file()
        print(" ! 원래 파일을 data_backup.json 으로 옮겨두었습니다.")
        cli.wait_enter()

    # 2. 메인 메뉴로 넘어가기
    cli.start(data)

    # 3. 종료
    cli.clear_screen()
    cli.print_line()
    print(" 관극로그를 종료합니다. 입력한 기록은 data.json 에 저장되어 있습니다.")
    cli.print_line()


if __name__ == "__main__":
    main()
