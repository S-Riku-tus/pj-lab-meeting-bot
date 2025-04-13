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
