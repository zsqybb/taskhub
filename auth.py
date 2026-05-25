"""认证与团队成员蓝图"""
from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db, query, get_one, execute
from decorators import login_required

auth_bp = Blueprint("auth", __name__)


# ── 注册 ───────────────────────────────────────────
@auth_bp.post("/api/auth/register")
def register():
    data = request.json
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""
    display_name = (data.get("display_name") or username).strip()

    if not username or len(username) < 2:
        return jsonify({"error": "用户名至少2个字符"}), 400
    if not email or "@" not in email:
        return jsonify({"error": "请输入有效的邮箱"}), 400
    if len(password) < 6:
        return jsonify({"error": "密码至少6位"}), 400

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM user WHERE username=%s OR email=%s", [username, email])
            if cur.fetchone():
                return jsonify({"error": "用户名或邮箱已存在"}), 409

            pw_hash = generate_password_hash(password)
            cur.execute(
                "INSERT INTO user (username, email, password_hash, display_name, role) VALUES (%s,%s,%s,%s,%s)",
                [username, email, pw_hash, display_name, "member"],
            )
            conn.commit()
            uid = cur.lastrowid

            # 尝试关联已有 team_member（按 email 模糊匹配）
            cur.execute("SELECT id FROM team_member WHERE email=%s OR name=%s", [email, display_name])
            tm = cur.fetchone()
            if tm:
                cur.execute("UPDATE team_member SET user_id=%s WHERE id=%s", [uid, tm["id"]])
                conn.commit()

            session["user_id"] = uid
            session["username"] = username
            session["display_name"] = display_name
            session["role"] = "member"
            session["member_id"] = tm["id"] if tm else None

        return jsonify({
            "ok": True, "user_id": uid, "username": username,
            "display_name": display_name, "role": "member",
            "member_id": session.get("member_id"),
        }), 201
    finally:
        conn.close()


# ── 登录 ───────────────────────────────────────────
@auth_bp.post("/api/auth/login")
def login():
    data = request.json
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify({"error": "请输入用户名和密码"}), 400

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, username, email, password_hash, display_name, role FROM user WHERE (username=%s OR email=%s) AND status=1",
                [username, username],
            )
            user = cur.fetchone()
            if not user or not check_password_hash(user["password_hash"], password):
                return jsonify({"error": "用户名或密码错误"}), 401

            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["display_name"] = user["display_name"] or user["username"]
            session["role"] = user["role"]

            # 关联 team_member：优先查 user_id FK，再按邮箱或姓名匹配
            cur.execute("SELECT id FROM team_member WHERE user_id=%s", [user["id"]])
            tm = cur.fetchone()
            if not tm:
                cur.execute(
                    "SELECT id FROM team_member WHERE email=%s OR name=%s",
                    [user["email"], user["display_name"]],
                )
                tm = cur.fetchone()
                if tm:
                    cur.execute("UPDATE team_member SET user_id=%s WHERE id=%s", [user["id"], tm["id"]])
                    conn.commit()
            session["member_id"] = tm["id"] if tm else None

        return jsonify({
            "ok": True,
            "user_id": user["id"],
            "username": user["username"],
            "display_name": user["display_name"] or user["username"],
            "role": user["role"],
            "member_id": session.get("member_id"),
        })
    finally:
        conn.close()


# ── 登出 ───────────────────────────────────────────
@auth_bp.post("/api/auth/logout")
def logout():
    session.clear()
    return jsonify({"ok": True})


# ── 当前用户 ──────────────────────────────────────
@auth_bp.get("/api/auth/me")
def me():
    if "user_id" not in session:
        return jsonify({"logged_in": False})
    return jsonify({
        "logged_in": True,
        "user_id": session["user_id"],
        "username": session["username"],
        "display_name": session.get("display_name"),
        "role": session.get("role"),
        "member_id": session.get("member_id"),
    })


# ── 个人中心 ───────────────────────────────────────
@auth_bp.put("/api/auth/profile")
@login_required
def update_profile():
    data = request.json
    display_name = (data.get("display_name") or "").strip()
    if not display_name:
        return jsonify({"error": "显示名称不能为空"}), 400
    execute("UPDATE user SET display_name=%s WHERE id=%s", [display_name, session["user_id"]])
    session["display_name"] = display_name
    return jsonify({"ok": True, "display_name": display_name})


@auth_bp.put("/api/auth/password")
@login_required
def change_password():
    data = request.json
    old_pw = data.get("old_password") or ""
    new_pw = data.get("new_password") or ""
    if len(new_pw) < 6:
        return jsonify({"error": "新密码至少6位"}), 400

    user = get_one("SELECT password_hash FROM user WHERE id=%s", [session["user_id"]])
    if not user or not check_password_hash(user["password_hash"], old_pw):
        return jsonify({"error": "原密码错误"}), 401

    pw_hash = generate_password_hash(new_pw)
    execute("UPDATE user SET password_hash=%s WHERE id=%s", [pw_hash, session["user_id"]])
    return jsonify({"ok": True, "msg": "密码已更新"})


@auth_bp.get("/api/auth/my-tasks")
@login_required
def my_tasks():
    member_id = session.get("member_id")
    if not member_id:
        return jsonify([])
    return jsonify(query(
        """SELECT t.*, p.name AS project_name, m.name AS milestone_name
           FROM task t
           JOIN project p ON t.project_id = p.id
           LEFT JOIN milestone m ON t.milestone_id = m.id
           WHERE t.assignee_id = %s AND t.status != 'done'
           ORDER BY t.priority DESC, t.due_date ASC""",
        [member_id],
    ))


@auth_bp.get("/api/auth/my-stats")
@login_required
def my_stats():
    member_id = session.get("member_id")
    if not member_id:
        return jsonify({"total_hours": 0, "task_count": 0, "recent_logs": []})
    stats = get_one(
        """SELECT SUM(hours) AS total_hours, COUNT(*) AS log_count
           FROM work_log WHERE member_id=%s""",
        [member_id],
    )
    task_count = get_one(
        "SELECT COUNT(*) AS c FROM task WHERE assignee_id=%s", [member_id]
    )
    recent = query(
        """SELECT wl.*, t.title AS task_title
           FROM work_log wl JOIN task t ON wl.task_id = t.id
           WHERE wl.member_id=%s ORDER BY wl.log_date DESC LIMIT 10""",
        [member_id],
    )
    return jsonify({
        "total_hours": float(stats["total_hours"] or 0),
        "log_count": stats["log_count"] or 0,
        "task_count": task_count["c"] if task_count else 0,
        "recent_logs": recent,
    })


# ── 团队成员 ───────────────────────────────────────
@auth_bp.get("/api/members")
@login_required
def list_members():
    return jsonify(query(
        "SELECT * FROM team_member WHERE status=1 ORDER BY role, id"
    ))
