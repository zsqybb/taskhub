"""TaskHub 配置"""
import os
import secrets
import pymysql.cursors

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "123456"),
    "database": os.getenv("DB_NAME", "task_hub"),
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
}

SECRET_KEY = os.getenv("SECRET_KEY") or secrets.token_hex(32)
