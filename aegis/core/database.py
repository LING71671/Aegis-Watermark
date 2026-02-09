import sqlite3
import os
from datetime import datetime

class TrackingDB:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(os.path.expanduser("~"), ".aegis_identity", "tracking.db")
        
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self._init_db()

    def _init_db(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS distributions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                recipient TEXT,
                watermark_id TEXT UNIQUE,
                key_used TEXT,
                timestamp DATETIME,
                status TEXT
            )
        ''')
        self.conn.commit()

    def log_distribution(self, filename, recipient, watermark_id, key_used, status="PENDING"):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO distributions (filename, recipient, watermark_id, key_used, timestamp, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (filename, recipient, watermark_id, key_used, datetime.now(), status))
        self.conn.commit()
        return cursor.lastrowid

    def update_status(self, dist_id, status):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE distributions SET status = ? WHERE id = ?', (status, dist_id))
        self.conn.commit()

    def find_by_watermark(self, watermark_id):
        cursor = self.conn.cursor()
        # 模糊匹配，因为提取出的水印 ID 可能会有轻微噪点干扰
        cursor.execute('SELECT * FROM distributions WHERE watermark_id LIKE ?', (f"%{watermark_id}%",))
        return cursor.fetchone()
