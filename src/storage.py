import json
import datetime
import os

# データファイルのパス
MEETING_DATA_FILE = "meeting_data.json"

# 会議データの初期値
DEFAULT_MEETING_DATA = {
    "meeting_time": "13:00",
    "meeting_day": "月曜日",
    "presenters": [],
    "next_meetings": []
}

def load_meeting_data():
    """会議データをJSONファイルから読み込む"""
    try:
        with open(MEETING_DATA_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # ファイルが存在しない場合、またはJSON解析エラーの場合はデフォルト値を返す
        return DEFAULT_MEETING_DATA.copy()

def save_meeting_data(data):
    """会議データをJSONファイルに保存する"""
    with open(MEETING_DATA_FILE, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

def get_next_meeting(meeting_data):
    """次回の会議情報を取得する"""
    # 日付でソート
    if meeting_data["next_meetings"]:
        sorted_meetings = sorted(
            meeting_data["next_meetings"], 
            key=lambda x: datetime.datetime.strptime(x["date"], "%Y年%m月%d日")
        )
        return sorted_meetings[0]
    return None

def parse_date(text):
    """テキストから日付を抽出する"""
    try:
        # 「yyyy年mm月dd日」形式の日付を検出
        import re
        date_pattern = r'(\d{4}年\d{1,2}月\d{1,2}日)'
        match = re.search(date_pattern, text)
        if match:
            return match.group(1)
    except Exception as e:
        print(f"日付解析エラー: {e}")
    return None

def add_or_update_meeting(meeting_data, date, time, presenters, presentation_type=None):
    """会議予定を追加または更新する"""
    # 既存の同じ日付の予定があるか検索
    for i, meeting in enumerate(meeting_data["next_meetings"]):
        if meeting["date"] == date:
            # 既存の予定を更新
            meeting_data["next_meetings"][i] = {
                "date": date,
                "time": time,
                "presenters": presenters,
                "presentation_type": presentation_type
            }
            return False  # 更新を示す
    
    # 新しい予定として追加
    meeting_data["next_meetings"].append({
        "date": date,
        "time": time,
        "presenters": presenters,
        "presentation_type": presentation_type
    })
    return True  # 新規追加を示す