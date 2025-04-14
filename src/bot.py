# src/bot.py
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from . import database
from dotenv import load_dotenv

# 発表タイプの定義
PRESENTATION_TYPES = ["進捗報告", "論文輪講", "技術共有", "アイデア提案", "その他"]

load_dotenv()  # .envファイルから環境変数を読み込む
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")


def send_reminder(DEFAULT_CHANNEL, SLACK_BOT_TOKEN):
    # Slack APIクライアント
    client = WebClient(token=SLACK_BOT_TOKEN)

    """リマインダーメッセージを送信する"""
    meeting_data = database.load_meeting_data()

    # 次回の会議情報を取得
    next_meeting = database.get_next_meeting()

    if next_meeting:
        meeting_date = next_meeting["meeting_date"]
        meeting_time = next_meeting["meeting_time"]
        presenters = next_meeting["presenters"]
        presentation_type = next_meeting["presentation_type"]
        meeting_id = next_meeting["id"]
    else:
        meeting_date = f"次の{meeting_data['meeting_day']}"
        meeting_time = meeting_data["meeting_time"]
        presenters = meeting_data["presenters"]
        presentation_type = "未指定"
        meeting_id = None

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
    future_meetings = meeting_data["next_meetings"]
    if len(future_meetings) > 1:  # 次回のミーティング以外にも予定がある場合
        message += "\n*今後の予定*:\n"
        for i, meeting in enumerate(future_meetings):
            if i == 0 and meeting_id:  # 次回のミーティングは既に上で表示済み
                continue
            presenters_str = ", ".join(meeting["presenters"]) if meeting["presenters"] else "未定"
            p_type = meeting["presentation_type"]
            message += f"• {meeting['date']} {meeting['time']}: {presenters_str} ({p_type})\n"

    try:
        response = client.chat_postMessage(
            channel=DEFAULT_CHANNEL,
            text=message,
            mrkdwn=True
        )
        print(f"メッセージ送信成功: {response['ts']}")

        # 使用済みの次回会議情報を削除
        if meeting_id:
            database.delete_meeting(meeting_id)

    except SlackApiError as e:
        print(f"エラー: {e.response['error']}")


def post_response(channel, text):
    """Slackチャンネルにメッセージを送信する"""
    try:
        client = WebClient(token=SLACK_BOT_TOKEN)
        response = client.chat_postMessage(
            channel=channel,
            text=text,
            mrkdwn=True
        )
        print(f"メッセージ送信成功: {response['ts']}")
        return response
    except SlackApiError as e:
        print(f"エラー: {e.response['error']}")
        return None
