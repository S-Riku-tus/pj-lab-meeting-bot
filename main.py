# main.py
import os
import sys
from flask import Flask, request, Response
from src import bot, commands, database
from dotenv import load_dotenv

load_dotenv()  # .envファイルから環境変数を読み込む

DEFAULT_CHANNEL = os.getenv("DEFAULT_CHANNEL")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")

app = Flask(__name__)


@app.route('/slack/events', methods=['POST'])
def slack_events():
    """Slackイベントを処理する"""
    data = request.json

    # URLの検証
    if "challenge" in data:
        return data["challenge"]

    # イベント処理
    if "event" in data:
        event = data["event"]

        # メンション時の処理
        if event.get("type") == "app_mention":
            commands.handle_mention(event)

    return Response(), 200


# アプリケーション初期化
def init_app():
    """アプリケーションを初期化する"""
    # データベースの初期化
    database.init_database()
    print("データベースを初期化しました")


# メイン関数 - GitHub Actionsから呼び出される
if __name__ == "__main__":
    # アプリケーション初期化
    init_app()

    # コマンドライン引数確認
    if len(sys.argv) > 1 and sys.argv[1] == "send_reminder":
        print("リマインド送信モードで実行します")
        bot.send_reminder(DEFAULT_CHANNEL, SLACK_BOT_TOKEN)
        print("リマインド送信が完了しました")
    else:
        # 開発環境でのFlaskサーバー起動
        print("Flaskサーバーを起動します (ポート:3000)")
        app.run(debug=True, port=3000)
