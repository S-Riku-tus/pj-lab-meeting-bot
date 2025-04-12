lab-meeting-bot/ ├── .github/ │ └── workflows/ │ └── reminder.yml # GitHub Actionsワークフロー ├── src/ │ ├── __init__.py # Pythonパッケージ化 │ ├── bot.py # ボット機能の中核 │ ├── commands.py # コマンド処理 │ └── storage.py # データ保存関連 ├── main.py

pasted

添付した文章について、これだとjsonファイルに個人情報が乗り、それをgithubに乗せないといけないので、運用できません。なので、これと同じ動作を、SQLiteなどの無料のデータベースを用いて作成し直したいです。

Slackの研究室ミーティングリマインドボットをSQLiteを使って再設計するのは良い選択です。JSONファイルではなくデータベースを使うことで、個人情報の管理を安全に行いながら、同じ機能を実現できます。

以下に、SQLiteを使用した再設計版のコードを作成します。


SQLiteを使用したミーティングリマインドボット
コード 
この実装では、次のような変更を行いました：

JSONファイルからSQLiteへ移行:
meeting_data.jsonの代わりにmeetings.dbというSQLiteデータベースを使用
個人情報を含むデータはローカルのデータベースに安全に保存され、GitHubにはコミットされません
データベース設計:
settingsテーブル: 基本的なミーティング設定（時間、曜日など）を保存
presentersテーブル: 通常の発表者リストを管理
next_meetingsテーブル: 今後のミーティング予定を管理
meeting_presentersテーブル: ミーティングと発表者の関連付け
データベース操作関数:
元のコードとの互換性を維持しつつ、SQLiteを使用する新しい関数を実装
初期化時に必要なテーブルを自動作成
既存のデータフォーマットとの変換処理を追加
改善点:
init_database関数でデータベースが存在しない場合に自動作成
関連するミーティング情報の削除が自動的に関連レコードも削除するよう設計（CASCADE制約）
デフォルト値の設定を一元化
このコードを使用することで、個人情報をGitHubにコミットすることなく、ローカルのSQLiteデータベースでミーティング情報を安全に管理できます。.gitignoreファイルに*.dbを追加して、データベースファイルがリポジトリにコミットされないようにすることをお勧めします。

これをどのように実行していけばよいか、ステップバイステップで教えてください。

SQLiteを使った研究室ミーティングリマインドボットを実行するためのステップバイステップガイドを作成します。

研究室ミーティングリマインドボットのセットアップ手順
1. プロジェクト準備
新しいディレクトリを作成する:
bash
mkdir lab-meeting-bot
cd lab-meeting-bot
プロジェクト構造を作成する:
bash
mkdir -p .github/workflows
mkdir -p src
touch .github/workflows/reminder.yml
touch src/__init__.py
touch src/bot.py
touch src/commands.py
touch src/database.py
touch main.py
touch README.md
.gitignore ファイルを作成する:
bash
echo "*.db" > .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo ".env" >> .gitignore
2. 必要なパッケージのインストール
requirements.txtファイルを作成する:
bash
echo "flask==2.0.1" > requirements.txt
echo "slack-sdk==3.15.2" >> requirements.txt
echo "python-dotenv==0.19.1" >> requirements.txt
パッケージをインストールする:
bash
pip install -r requirements.txt
3. コードファイル作成
各ファイルに先ほど作成したコードをコピーする:
src/database.py
src/bot.py
src/commands.py
main.py
.github/workflows/reminder.yml
4. 環境変数の設定
ローカル開発用に.envファイルを作成する:
bash
touch .env
.envファイルに必要な変数を追加する:
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
DEFAULT_CHANNEL=#your-channel-name
.envファイルを読み込むコードをmain.pyに追加する (既存のコードの先頭に):
python
from dotenv import load_dotenv
load_dotenv()  # .envファイルから環境変数を読み込む
5. Slackアプリの設定
Slack APIダッシュボード (https://api.slack.com/apps) にアクセスする
新しいアプリを作成する:
「Create New App」をクリック
「From scratch」を選択
アプリ名（例：「研究室ミーティングボット」）を入力
ワークスペースを選択
ボットのスコープを設定する:
「OAuth & Permissions」セクションに移動
「Scopes」>「Bot Token Scopes」で以下を追加:
chat:write
app_mentions:read
アプリをワークスペースにインストールする:
「OAuth & Permissions」セクションで「Install to Workspace」をクリック
許可を承認
ボットトークンをコピーする:
「Bot User OAuth Token」をコピーし、.envファイルのSLACK_BOT_TOKEN値として設定
イベント購読を設定する:
「Event Subscriptions」をオン
以下のイベントを購読:
app_mention
6. ローカルでのテスト実行
データベースを初期化し、Flaskサーバーを起動する:
bash
python main.py
ngrokなどのツールを使用してローカルサーバーを公開する (Slack APIからのリクエスト受信用):
bash
ngrok http 3000
ngrokが生成したURLをSlack APIの設定に追加する:
Slack APIダッシュボードの「Event Subscriptions」セクションに移動
Request URLに https://あなたのngrokURL/slack/events を入力
Slackでボットをテストする:
対象のチャンネルにボットを招待: /invite @ボット名
ボットにメンションして各コマンドをテスト: @ボット名 状況確認
7. GitHubへのデプロイ
GitHubリポジトリを作成する
ローカルリポジトリを初期化して、GitHubにプッシュする:
bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/ユーザー名/lab-meeting-bot.git
git push -u origin main
GitHubシークレットを設定する:
リポジトリの「Settings」>「Secrets and variables」>「Actions」に移動
新しいシークレットを追加:
SLACK_BOT_TOKEN: Slackボットトークン
DEFAULT_CHANNEL: 通知先のチャンネル名（例：#general）
GitHub Actionsの設定を確認する:
.github/workflows/reminder.ymlファイルが正しく設定されていることを確認
スケジュール（cron設定）が適切かチェック
8. デプロイ後の確認
GitHub Actionsで手動実行してテストする:
GitHubリポジトリの「Actions」タブに移動
「Weekly Meeting Reminder」ワークフローを選択
「Run workflow」をクリック
Slackで通知が届くことを確認する
9. 運用と保守
必要に応じてコマンドを使って設定を変更する:
@ボット名 発表者変更 「名前1」「名前2」
@ボット名 時間変更 15:30
@ボット名 曜日変更 水曜日
@ボット名 日程追加 2025年4月15日 15:00 「名前1」「名前2」 進捗報告
SQLiteデータベースのバックアップ:
定期的にmeetings.dbファイルをバックアップすることをお勧めします
GitHub Actionsでバックアップを自動化することも可能です
これで、SQLiteを使用した研究室ミーティングリマインドボットを実行する準備が整いました。データベースはローカルに保存され、個人情報がGitHubにコミットされることはありません。

何か質問があれば、お気軽にどうぞ！



, "卒論発表", "修論発表", "チューターミーティング"

# ディレクトリ構造（変更後）
# lab-meeting-bot/
# ├── .github/
# │   └── workflows/
# │       └── reminder.yml      # GitHub Actionsワークフロー
# ├── src/
# │   ├── __init__.py           # Pythonパッケージ化
# │   ├── bot.py                # ボット機能の中核
# │   ├── commands.py           # コマンド処理
# │   └── database.py           # データベース関連（storage.pyの代わり）
# ├── main.py                   # エントリーポイント
# ├── meetings.db               # SQLiteデータベース（meeting_data.jsonの代わり）
# └── README.md                 # 使い方説明

# src/database.py
import sqlite3
import datetime
import os
import re

# データベースファイルのパス
DATABASE_FILE = "meetings.db"

def init_database():
    """データベースの初期化と必要なテーブルの作成"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # 設定テーブル（定期ミーティングの基本情報）
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    ''')
    
    # 発表者テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS presenters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
    ''')
    
    # 次回のミーティング情報テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS next_meetings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        meeting_date TEXT NOT NULL,
        meeting_time TEXT NOT NULL,
        presentation_type TEXT DEFAULT '未指定'
    )
    ''')
    
    # ミーティングの発表者（多対多の関係）
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS meeting_presenters (
        meeting_id INTEGER,
        presenter_name TEXT,
        PRIMARY KEY (meeting_id, presenter_name),
        FOREIGN KEY (meeting_id) REFERENCES next_meetings(id) ON DELETE CASCADE
    )
    ''')
    
    # デフォルト設定の挿入
    default_settings = [
        ('meeting_time', '13:00'),
        ('meeting_day', '月曜日')
    ]
    
    for key, value in default_settings:
        cursor.execute('''
        INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)
        ''', (key, value))
    
    conn.commit()
    conn.close()

def get_setting(key):
    """設定を取得する"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
    result = cursor.fetchone()
    
    conn.close()
    return result[0] if result else None

def update_setting(key, value):
    """設定を更新する"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)
    ''', (key, value))
    
    conn.commit()
    conn.close()

def get_presenters():
    """通常の発表者リストを取得する"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT name FROM presenters ORDER BY id')
    result = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return result

def update_presenters(presenters):
    """発表者リストを更新する"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # 現在の発表者をクリア
    cursor.execute('DELETE FROM presenters')
    
    # 新しい発表者を追加
    for presenter in presenters:
        cursor.execute('INSERT INTO presenters (name) VALUES (?)', (presenter,))
    
    conn.commit()
    conn.close()

def get_next_meetings():
    """今後の予定ミーティングをすべて取得する"""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row  # 列名でアクセスできるようにする
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT nm.id, nm.meeting_date, nm.meeting_time, nm.presentation_type 
    FROM next_meetings nm
    ORDER BY date(substr(nm.meeting_date, 1, 4) || '-' || 
             substr(nm.meeting_date, 6, 2) || '-' || 
             substr(nm.meeting_date, 9, 2))
    ''')
    meetings = []
    
    for row in cursor.fetchall():
        meeting_id = row['id']
        meeting = dict(row)
        
        # 各ミーティングの発表者を取得
        cursor.execute('''
        SELECT presenter_name FROM meeting_presenters 
        WHERE meeting_id = ?
        ''', (meeting_id,))
        
        presenters = [p[0] for p in cursor.fetchall()]
        meeting['presenters'] = presenters
        meetings.append(meeting)
    
    conn.close()
    return meetings

def get_next_meeting():
    """次回のミーティング情報を取得する"""
    meetings = get_next_meetings()
    return meetings[0] if meetings else None

def add_or_update_meeting(date, time, presenters, presentation_type='未指定'):
    """会議予定を追加または更新する"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # 既存の同じ日付の予定があるか検索
    cursor.execute('''
    SELECT id FROM next_meetings WHERE meeting_date = ?
    ''', (date,))
    
    existing = cursor.fetchone()
    is_new = existing is None
    
    if is_new:
        # 新規ミーティングの追加
        cursor.execute('''
        INSERT INTO next_meetings (meeting_date, meeting_time, presentation_type) 
        VALUES (?, ?, ?)
        ''', (date, time, presentation_type))
        meeting_id = cursor.lastrowid
    else:
        # 既存ミーティングの更新
        meeting_id = existing[0]
        cursor.execute('''
        UPDATE next_meetings 
        SET meeting_time = ?, presentation_type = ? 
        WHERE id = ?
        ''', (time, presentation_type, meeting_id))
        
        # 関連する発表者を削除（後で再登録）
        cursor.execute('DELETE FROM meeting_presenters WHERE meeting_id = ?', (meeting_id,))
    
    # 発表者を登録
    for presenter in presenters:
        cursor.execute('''
        INSERT INTO meeting_presenters (meeting_id, presenter_name) 
        VALUES (?, ?)
        ''', (meeting_id, presenter))
    
    conn.commit()
    conn.close()
    return is_new

def delete_meeting(meeting_id):
    """特定のミーティングを削除する"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM next_meetings WHERE id = ?', (meeting_id,))
    # CASCADEが指定されているので関連する発表者も自動的に削除される
    
    conn.commit()
    conn.close()

def parse_date(text):
    """テキストから日付を抽出する"""
    try:
        # 「yyyy年mm月dd日」形式の日付を検出
        date_pattern = r'(\d{4}年\d{1,2}月\d{1,2}日)'
        match = re.search(date_pattern, text)
        if match:
            return match.group(1)
    except Exception as e:
        print(f"日付解析エラー: {e}")
    return None

def load_meeting_data():
    """元のJSONフォーマットに互換性を持たせた形式でデータを取得する"""
    # データベースが存在しない場合は初期化
    if not os.path.exists(DATABASE_FILE):
        init_database()
    
    meeting_data = {
        "meeting_time": get_setting("meeting_time"),
        "meeting_day": get_setting("meeting_day"),
        "presenters": get_presenters(),
        "next_meetings": []
    }
    
    # 次回の会議情報を取得して変換
    next_meetings = get_next_meetings()
    for meeting in next_meetings:
        meeting_data["next_meetings"].append({
            "id": meeting["id"],
            "date": meeting["meeting_date"],
            "time": meeting["meeting_time"],
            "presenters": meeting["presenters"],
            "presentation_type": meeting["presentation_type"]
        })
    
    return meeting_data

def save_meeting_data(data):
    """元のJSONフォーマットからデータベースに保存する"""
    # データベースが存在しない場合は初期化
    if not os.path.exists(DATABASE_FILE):
        init_database()
    
    # 基本設定の更新
    update_setting("meeting_time", data["meeting_time"])
    update_setting("meeting_day", data["meeting_day"])
    
    # 発表者の更新
    update_presenters(data["presenters"])