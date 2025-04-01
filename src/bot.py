import os
import re
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from . import storage

# Slack APIクライアント
client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
DEFAULT_CHANNEL = os.environ.get("DEFAULT_CHANNEL", "#general")

# 発表タイプの定義
PRESENTATION_TYPES = ["進捗報告", "論文輪講", "技術共有", "アイデア提案", "その他"]

def send_reminder():
    """リマインダーメッセージを送信する"""
    meeting_data = storage.load_meeting_data()
    
    # 次回の会議情報を取得
    next_meeting = storage.get_next_meeting(meeting_data)
    
    if next_meeting:
        meeting_date = next_meeting["date"]
        meeting_time = next_meeting["time"]
        presenters = next_meeting["presenters"]
        presentation_type = next_meeting.get("presentation_type", "未指定")
    else:
        meeting_date = f"次の{meeting_data['meeting_day']}"
        meeting_time = meeting_data["meeting_time"]
        presenters = meeting_data["presenters"]
        presentation_type = "未指定"
    
    # メッセージテキストの作成
    message = f"*研究室ミーティングのお知らせ*\n"
    message += f"日時: {meeting_date} {meeting_time}\n"
    message += f"発表タイプ: {presentation_type}\n\n"
    
    if presenters:
        message += "*発表者*:\n"
        for i, presenter in enumerate(presenters, 1):
            message += f"{i}. {presenter}\n"
    else:
        message += "発表者は未定です。\n"
    
    # 今後の予定がある場合は追加
    future_meetings = [m for m in meeting_data["next_meetings"] if m != next_meeting]
    if future_meetings:
        message += "\n*今後の予定*:\n"
        for meeting in future_meetings:
            presenters_str = ", ".join(meeting["presenters"]) if meeting["presenters"] else "未定"
            p_type = meeting.get("presentation_type", "未指定")
            message += f"• {meeting['date']} {meeting['time']}: {presenters_str} ({p_type})\n"
    
    try:
        response = client.chat_postMessage(
            channel=DEFAULT_CHANNEL,
            text=message,
            mrkdwn=True
        )
        print(f"メッセージ送信成功: {response['ts']}")
        
        # 使用済みの次回会議情報を削除
        if next_meeting in meeting_data["next_meetings"]:
            meeting_data["next_meetings"].remove(next_meeting)
            storage.save_meeting_data(meeting_data)
            
    except SlackApiError as e:
        print(f"エラー: {e.response['error']}")

def post_response(channel, text):
    """Slackチャンネルにメッセージを送信する"""
    try:
        client.chat_postMessage(
            channel=channel,
            text=text,
            mrkdwn=True
        )
        return True
    except SlackApiError as e:
        print(f"エラー: {e.response['error']}")
        return False