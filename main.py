import os
import sys
from flask import Flask, request, Response
from src import bot, commands

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

# メイン関数 - GitHub Actionsから呼び出される
if __name__ == "__main__":
    # コマンドライン引数確認
    if len(sys.argv) > 1 and sys.argv[1] == "send_reminder":
        bot.send_reminder()
    else:
        # 開発環境でのFlaskサーバー起動
        app.run(debug=True, port=3000)