"""认证与团队成员蓝图"""
from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db, query, get_one, execute
from decorators import login_required, generate_csrf_token

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

            # 自动创建 team_member 档案
            cur.execute(
                "INSERT INTO team_member (name, email, role, user_id) VALUES (%s, %s, %s, %s)",
                [display_name, email, "member", uid],
            )
            conn.commit()
            member_id = cur.lastrowid

            session["user_id"] = uid
            session["username"] = username
            session["display_name"] = display_name
            session["role"] = "member"
            session["member_id"] = member_id

        return jsonify({
            "ok": True, "user_id": uid, "username": username,
            "display_name": display_name, "role": "member",
            "member_id": member_id,
            "csrf_token": generate_csrf_token(),
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

            # 关联 team_member：优先查 user_id FK，再按邮箱匹配，最后自动创建
            cur.execute("SELECT id FROM team_member WHERE user_id=%s", [user["id"]])
            tm = cur.fetchone()
            if not tm:
                cur.execute(
                    "SELECT id, user_id FROM team_member WHERE email=%s",
                    [user["email"]],
                )
                tm = cur.fetchone()
                if tm and (tm["user_id"] is None or tm["user_id"] == user["id"]):
                    cur.execute("UPDATE team_member SET user_id=%s WHERE id=%s", [user["id"], tm["id"]])
                    conn.commit()
                elif tm and tm["user_id"] != user["id"]:
                    tm = None  # 属于其他用户，不抢夺
            if not tm:
                try:
                    cur.execute(
                        "INSERT INTO team_member (name, email, role, user_id) VALUES (%s, %s, %s, %s)",
                        [user["display_name"] or user["username"], user["email"], user["role"], user["id"]],
                    )
                    conn.commit()
                    tm = {"id": cur.lastrowid}
                except Exception:
                    cur.execute("SELECT id, user_id FROM team_member WHERE email=%s", [user["email"]])
                    tm = cur.fetchone()
                    if tm and (tm["user_id"] is None or tm["user_id"] == user["id"]):
                        cur.execute("UPDATE team_member SET user_id=%s WHERE id=%s", [user["id"], tm["id"]])
                        conn.commit()
            session["member_id"] = tm["id"]

        return jsonify({
            "ok": True,
            "user_id": user["id"],
            "username": user["username"],
            "display_name": user["display_name"] or user["username"],
            "role": user["role"],
            "member_id": session.get("member_id"),
            "csrf_token": generate_csrf_token(),
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
    member = get_one(
        "SELECT name, email, phone, department FROM team_member WHERE id=%s",
        [session.get("member_id")],
    )
    return jsonify({
        "logged_in": True,
        "user_id": session["user_id"],
        "username": session["username"],
        "display_name": session.get("display_name"),
        "role": session.get("role"),
        "member_id": session.get("member_id"),
        "member_name": (member["name"] if member else None) or session.get("display_name", ""),
        "email": (member["email"] if member else None) or "",
        "phone": (member["phone"] if member else None) or "",
        "department": (member["department"] if member else None) or "",
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

    member_id = session.get("member_id")
    name = (data.get("name") or display_name).strip()
    email = (data.get("email") or "").strip()
    phone = (data.get("phone") or "").strip()
    department = (data.get("department") or "").strip()

    if member_id:
        # 检查 email 是否与其他 team_member 或 user 冲突
        if email:
            dup = get_one(
                "SELECT id FROM team_member WHERE email=%s AND id!=%s",
                [email, member_id],
            )
            if dup:
                return jsonify({"error": "该邮箱已被其他团队成员使用"}), 409
            dup_user = get_one(
                "SELECT id FROM user WHERE email=%s AND id!=%s",
                [email, session["user_id"]],
            )
            if dup_user:
                return jsonify({"error": "该邮箱已被其他用户使用"}), 409
        execute(
            "UPDATE team_member SET name=%s, email=%s, phone=%s, department=%s WHERE id=%s",
            [name, email, phone, department, member_id],
        )
    return jsonify({
        "ok": True, "display_name": display_name,
        "member_name": name, "email": email, "phone": phone, "department": department,
    })


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
        "SELECT * FROM team_member WHERE user_id=%s AND status=1 ORDER BY role, id",
        [session["user_id"]],
    ))
