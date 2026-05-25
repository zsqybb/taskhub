"""认证装饰器"""
from functools import wraps
import secrets
from flask import session, jsonify, redirect, url_for, request


def login_required(f):
    """API 装饰器：返回 401 JSON"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "请先登录"}), 401
        return f(*args, **kwargs)
    return decorated


def page_login_required(f):
    """页面装饰器：重定向到 /login"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """API 装饰器：仅 admin 可调用"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "请先登录"}), 401
        if session.get("role") != "admin":
            return jsonify({"error": "仅管理员可执行此操作"}), 403
        return f(*args, **kwargs)
    return decorated


def generate_csrf_token():
    """生成 CSRF token 并存入 session"""
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(32)
    return session["csrf_token"]
