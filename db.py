"""数据库工具模块 — 连接池、查询、序列化"""
import pymysql
from datetime import datetime, date
from decimal import Decimal
from dbutils.pooled_db import PooledDB
from config import DB_CONFIG

_pool = None


def _get_pool():
    global _pool
    if _pool is None:
        _pool = PooledDB(
            creator=pymysql,
            mincached=2,
            maxcached=10,
            maxconnections=20,
            blocking=True,
            ping=1,
            **DB_CONFIG,
        )
    return _pool


def get_db():
    return _get_pool().connection()


def _serialize(val):
    if isinstance(val, (datetime, date)):
        return val.isoformat()
    if isinstance(val, Decimal):
        return float(val)
    return val


def row_to_dict(row):
    """将 pymysql DictCursor 行中的特殊类型序列化"""
    if row is None:
        return None
    return {col: _serialize(val) for col, val in row.items()}


def query(sql, args=None):
    """SELECT 查询，返回 list[dict]"""
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, args)
            return [row_to_dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def get_one(sql, args=None):
    """SELECT 查询，返回单行 dict 或 None"""
    rows = query(sql, args)
    return rows[0] if rows else None


def execute(sql, args=None):
    """INSERT / UPDATE / DELETE，提交事务并返回 lastrowid"""
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, args)
            conn.commit()
            return cur.lastrowid
    finally:
        conn.close()
