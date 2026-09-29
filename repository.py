# ============================================================
# repository.py - data.json 불러오고 저장하는 파일 (MOD-006)
#
# 프로그램을 켤 때 한 번만 불러와서 딕셔너리로 메모리에 올려두고,
# 등록 / 수정 / 삭제를 할 때마다 전체를 다시 덮어써서 저장한다.
# 그래서 프로그램이 갑자기 꺼져도 그 전까지 넣은 기록은 남아있다.
# ============================================================

import json
import os

DATA_FILE = "data.json"                 # 저장 파일 이름
BACKUP_FILE = "data_backup.json"        # 파일이 깨졌을 때 옮겨둘 이름


# 데이터 불러오기. (데이터, 상태) 로 돌려준다
# 상태는 "정상" / "새파일" / "오류" 셋 중 하나다
def load_data():
    # 파일이 없으면 빈 데이터로 새로 만든다
    if os.path.exists(DATA_FILE) == False:
        data = {"performances": []}
        save_data(data)
        return data, "새파일"

    try:
        f = open(DATA_FILE, "r", encoding="utf-8")
        data = json.load(f)
        f.close()
    except:
        # 파일이 깨져서 못 읽는 경우
        return None, "오류"

    # 파일은 읽었는데 안에 들어있는 모양이 이상한 경우도 오류로 본다
    if type(data) != dict:
        return None, "오류"
    if "performances" not in data:
        return None, "오류"
    if type(data["performances"]) != list:
        return None, "오류"

    return data, "정상"


# 파일이 깨졌을 때 새로 시작하기
# 원래 파일은 지우지 않고 data_backup.json 으로 이름만 바꿔서 남겨둔다
def start_new_file():
    if os.path.exists(DATA_FILE) == True:
        if os.path.exists(BACKUP_FILE) == True:
            os.remove(BACKUP_FILE)
        os.rename(DATA_FILE, BACKUP_FILE)

    data = {"performances": []}
    save_data(data)
    return data


# 데이터 저장하기 (메모리에 있는 걸 통째로 덮어쓴다)
# open(파일, "w") 를 하는 순간 원래 내용이 지워지기 때문에,
# 파일을 열고 나서 오류가 나면 data.json 이 반만 써진 채로 깨진다.
# 그래서 저장할 내용을 먼저 다 만들어 보고, 문제가 없을 때만 파일을 연다.
# 저장이 잘 되면 True, 실패하면 False 를 돌려준다.
def save_data(data):
    # 1. 저장할 내용을 먼저 글자로 다 만들어 본다
    #    여기서 실패하면 data.json 은 아직 열지도 않았으니까 그대로 남는다
    try:
        text = json.dumps(data, ensure_ascii=False, indent=2)
        text.encode("utf-8")        # 파일에 쓸 수 있는 글자인지 미리 확인
    except:
        return False

    # 2. 문제가 없으면 그때 파일에 쓴다
    try:
        f = open(DATA_FILE, "w", encoding="utf-8")
        f.write(text)
        f.close()
        return True
    except:
        return False
