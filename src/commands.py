# src/commands.py
import re
from . import database
from . import bot


def handle_mention(event):
    """メンションに応答する"""
    text = event.get("text", "")
    channel = event.get("channel")

    meeting_data = database.load_meeting_data()

    # 発表者変更
    if "発表者変更" in text or "発表者を変更" in text:
        response_text = change_presenters(text, meeting_data)

    # 時間変更
    elif "時間変更" in text or "時間を変更" in text:
        response_text = change_time(text, meeting_data)

    # 曜日変更
    elif "曜日変更" in text or "曜日を変更" in text:
        response_text = change_day(text, meeting_data)

    # 今後の日程追加
    elif "日程追加" in text or "予定追加" in text:
        response_text = add_schedule(text, meeting_data)

    # 状況確認
    elif "状況" in text or "確認" in text:
        response_text = check_status(meeting_data)

    # 手動リマインド送信
    elif "リマインド送信" in text or "リマインド" in text:
        bot.send_reminder()
        response_text = "リマインドを送信しました。"

    # ヘルプ
    else:
        response_text = get_help_text()

    bot.post_response(channel, response_text)


def change_presenters(text, meeting_data):
    """発表者を変更する"""
    # 発表者リストを抽出
    presenters = re.findall(r'「(.+?)」', text)
    if not presenters:
        # 「」がない場合は空白で分割して最後の部分を取得
        parts = text.split()
        if len(parts) > 3:  # "発表者変更 名前1 名前2..." を想定
            presenters = parts[2:]

    if presenters:
        database.update_presenters(presenters)
        return f"発表者を変更しました: {', '.join(presenters)}"
    else:
        return "発表者を指定してください。例: @ミーティングボット 発表者変更 「田中」「鈴木」"


def change_time(text, meeting_data):
    """ミーティング時間を変更する"""
    time_match = re.search(r'(\d{1,2}:\d{2})', text)
    if time_match:
        new_time = time_match.group(1)
        database.update_setting("meeting_time", new_time)
        return f"ミーティング時間を {new_time} に変更しました"
    else:
        return "新しい時間を指定してください。例: @ミーティングボット 時間変更 14:30"


def change_day(text, meeting_data):
    """ミーティング曜日を変更する"""
    days = ["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"]
    for day in days:
        if day in text:
            database.update_setting("meeting_day", day)
            return f"ミーティング曜日を {day} に変更しました"
    return "新しい曜日を指定してください。例: @ミーティングボット 曜日変更 水曜日"


def add_schedule(text, meeting_data):
    """特定の日程を追加する"""
    date = database.parse_date(text)
    time_match = re.search(r'(\d{1,2}:\d{2})', text)
    presenters = re.findall(r'「(.+?)」', text)

    # 発表タイプの検出
    presentation_type = "未指定"
    for ptype in bot.PRESENTATION_TYPES:
        if ptype in text:
            presentation_type = ptype
            break

    if date and time_match:
        new_time = time_match.group(1)
        is_new = database.add_or_update_meeting(
            date, new_time, presenters, presentation_type
        )

        presenters_str = ", ".join(presenters) if presenters else "未定"
        action = "追加" if is_new else "更新"
        return f"{date} {new_time} の予定を{action}しました。\n発表者: {presenters_str}\n発表タイプ: {presentation_type}"
    else:
        return "日付と時間を指定してください。例: @ミーティングボット 日程追加 2025年4月15日 15:00 「山田」「佐藤」 進捗報告"


def check_status(meeting_data):
    """現在の設定状況を確認する"""
    next_meeting = database.get_next_meeting()

    response_text = "*現在の設定*\n"
    response_text += f"定期ミーティング: 毎週{meeting_data['meeting_day']} {meeting_data['meeting_time']}\n"
    response_text += f"通常の発表者: {', '.join(meeting_data['presenters']) if meeting_data['presenters'] else '未定'}\n\n"

    if meeting_data["next_meetings"]:
        response_text += "*今後の予定*:\n"
        for meeting in meeting_data["next_meetings"]:
            presenters_str = ", ".join(meeting["presenters"]) if meeting["presenters"] else "未定"
            p_type = meeting["presentation_type"]
            response_text += f"• {meeting['date']} {meeting['time']}: {presenters_str} ({p_type})\n"
    else:
        response_text += "今後の特別な予定はありません。"

    return response_text


def get_help_text():
    """ヘルプテキストを取得する"""
    return """
*使い方*:
• @ミーティングボット 発表者変更 「名前1」「名前2」...: 発表者を変更します
• @ミーティングボット 時間変更 15:30: ミーティング時間を変更します
• @ミーティングボット 曜日変更 水曜日: ミーティング曜日を変更します
• @ミーティングボット 日程追加 2025年4月15日 15:00 「名前1」「名前2」... 進捗報告: 特定の日時の予定を追加します
  - 発表タイプ: 進捗報告、論文輪講、技術共有、アイデア提案、その他
• @ミーティングボット 状況確認: 現在の設定と今後の予定を表示します
• @ミーティングボット リマインド送信: リマインドを手動で送信します
"""