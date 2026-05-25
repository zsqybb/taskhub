"""任务、工时、评论蓝图"""
from datetime import datetime
from flask import Blueprint, request, jsonify, session
from db import query, get_one, execute, execute_affected
from decorators import login_required
from activities import log
from utils import opt_none, update_project_progress, parse_int

tasks_bp = Blueprint("tasks", __name__)


# ── 任务 CRUD ──────────────────────────────────────
@tasks_bp.get("/api/tasks")
@login_required
def list_tasks():
    project_id = request.args.get("project_id")
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()
    assignee_id = request.args.get("assignee_id", "").strip()
    page = parse_int(request.args.get("page", 1), 1)
    per_page = parse_int(request.args.get("per_page", 20), 20, 5, 100)
    offset = (page - 1) * per_page

    sql = """
        SELECT t.*, tm.name AS assignee_name, m.name AS milestone_name
        FROM task t
        JOIN project p ON t.project_id = p.id
        LEFT JOIN team_member tm ON t.assignee_id = tm.id
        LEFT JOIN milestone m ON t.milestone_id = m.id
        WHERE p.owner_id = %s
    """
    count_sql = "SELECT COUNT(*) AS total FROM task t JOIN project p ON t.project_id = p.id WHERE p.owner_id = %s"
    conditions = []
    args = [session["user_id"]]

    if project_id:
        conditions.append("t.project_id = %s")
        args.append(project_id)
    if search:
        conditions.append("t.title LIKE %s")
        args.append(f"%{search}%")
    if status:
        conditions.append("t.status = %s")
        args.append(status)
    if assignee_id:
        conditions.append("t.assignee_id = %s")
        args.append(assignee_id)

    if conditions:
        where = " AND " + " AND ".join(conditions)
        sql += where
        count_sql += where

    sql += " ORDER BY t.sort_order, t.id LIMIT %s OFFSET %s"
    args += [per_page, offset]

    rows = query(sql, args)
    total = get_one(count_sql, args[:-2])["total"]

    return jsonify({"data": rows, "total": total, "page": page, "per_page": per_page})


@tasks_bp.get("/api/tasks/<int:tid>")
@login_required
def get_task(tid):
    row = get_one(
        """SELECT t.*, tm.name AS assignee_name, m.name AS milestone_name
           FROM task t
           JOIN project p ON t.project_id = p.id
           LEFT JOIN team_member tm ON t.assignee_id = tm.id
           LEFT JOIN milestone m ON t.milestone_id = m.id
           WHERE t.id = %s AND p.owner_id = %s""",
        [tid, session["user_id"]],
    )
    if not row:
        return jsonify({"error": "任务不存在"}), 404
    return jsonify(row)


@tasks_bp.post("/api/tasks")
@login_required
def create_task():
    data = request.json
    title = (data.get("title") or "").strip()
    project_id = data.get("project_id")
    if not title:
        return jsonify({"error": "任务标题不能为空"}), 400
    if not project_id:
        return jsonify({"error": "请指定所属项目"}), 400
    proj = get_one("SELECT id FROM project WHERE id=%s AND owner_id=%s",
                   [project_id, session["user_id"]])
    if not proj:
        return jsonify({"error": "项目不存在"}), 404
    tid = execute(
        """INSERT INTO task (project_id, milestone_id, title, description, status, priority,
           assignee_id, estimated_hours, start_date, due_date, sort_order)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        [project_id, opt_none(data.get("milestone_id")), title, opt_none(data.get("description")),
         data.get("status", "todo"), data.get("priority", 2), opt_none(data.get("assignee_id")),
         opt_none(data.get("estimated_hours")), opt_none(data.get("start_date")), opt_none(data.get("due_date")),
         data.get("sort_order", 0)],
    )
    update_project_progress(project_id)
    log("创建了任务", "task", tid, f"创建了任务「{title}」")
    return jsonify({"id": tid}), 201


@tasks_bp.put("/api/tasks/<int:tid>")
@login_required
def update_task(tid):
    data = request.json
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"error": "任务标题不能为空"}), 400
    task = get_one("""SELECT t.id, t.project_id FROM task t JOIN project p ON t.project_id = p.id
                      WHERE t.id = %s AND p.owner_id = %s""",
                   [tid, session["user_id"]])
    if not task:
        return jsonify({"error": "任务不存在"}), 404
    new_status = data.get("status")
    completed_at = data.get("completed_at")
    if not completed_at and new_status == "done":
        completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    execute(
        """UPDATE task SET title=%s, description=%s, status=%s, priority=%s, assignee_id=%s,
           estimated_hours=%s, actual_hours=%s, milestone_id=%s, start_date=%s, due_date=%s,
           completed_at=%s, sort_order=%s WHERE id=%s""",
        [title, opt_none(data.get("description")), new_status, data.get("priority"),
         opt_none(data.get("assignee_id")), opt_none(data.get("estimated_hours")), opt_none(data.get("actual_hours")),
         opt_none(data.get("milestone_id")), opt_none(data.get("start_date")), opt_none(data.get("due_date")),
         opt_none(completed_at), data.get("sort_order", 0), tid],
    )
    log("更新了任务", "task", tid, f"更新了任务「{data['title']}」")
    update_project_progress(task["project_id"])
    return jsonify({"ok": True})


@tasks_bp.delete("/api/tasks/<int:tid>")
@login_required
def delete_task(tid):
    task = get_one("""SELECT t.project_id, t.title FROM task t
                      JOIN project p ON t.project_id = p.id
                      WHERE t.id = %s AND p.owner_id = %s""",
                   [tid, session["user_id"]])
    if not task:
        return jsonify({"error": "任务不存在"}), 404
    execute("DELETE FROM task WHERE id=%s", [tid])
    update_project_progress(task["project_id"])
    log("删除了任务", "task", tid, f"删除了任务「{task['title']}」")
    return jsonify({"ok": True})


# ── 工时记录 ───────────────────────────────────────
@tasks_bp.get("/api/worklogs")
@login_required
def list_worklogs():
    task_id = request.args.get("task_id")
    member_id = request.args.get("member_id")
    conditions = []
    args = []

    if task_id:
        conditions.append("wl.task_id = %s")
        args.append(task_id)
    if member_id:
        conditions.append("wl.member_id = %s")
        args.append(member_id)

    sql = """
        SELECT wl.*, tm.name AS member_name, t.title AS task_title
        FROM work_log wl
        JOIN team_member tm ON wl.member_id = tm.id
        JOIN task t ON wl.task_id = t.id
        JOIN project p ON t.project_id = p.id
        WHERE p.owner_id = %s
    """
    args.insert(0, session["user_id"])
    if conditions:
        sql += " AND " + " AND ".join(conditions)
    sql += " ORDER BY wl.log_date DESC, wl.id DESC"

    return jsonify(query(sql, args))


@tasks_bp.post("/api/worklogs")
@login_required
def create_worklog():
    data = request.json
    task = get_one("""SELECT t.id FROM task t JOIN project p ON t.project_id = p.id
                      WHERE t.id = %s AND p.owner_id = %s""",
                   [data["task_id"], session["user_id"]])
    if not task:
        return jsonify({"error": "任务不存在"}), 404
    wid = execute(
        "INSERT INTO work_log (task_id, member_id, hours, log_date, description) VALUES (%s,%s,%s,%s,%s)",
        [data["task_id"], data["member_id"], data["hours"], data["log_date"], data.get("description")],
    )
    # 更新任务实际工时
    row = get_one("SELECT SUM(hours) AS total FROM work_log WHERE task_id=%s", [data["task_id"]])
    if row and row["total"] is not None:
        execute("UPDATE task SET actual_hours=%s WHERE id=%s", [row["total"], data["task_id"]])
    return jsonify({"id": wid}), 201


# ── 评论 ───────────────────────────────────────────
@tasks_bp.get("/api/comments")
@login_required
def list_comments():
    task_id = request.args.get("task_id")
    if not task_id:
        return jsonify([])
    return jsonify(query(
        """SELECT c.*, tm.name AS member_name
           FROM comment c
           JOIN team_member tm ON c.member_id = tm.id
           JOIN task t ON c.task_id = t.id
           JOIN project p ON t.project_id = p.id
           WHERE c.task_id = %s AND p.owner_id = %s
           ORDER BY c.created_at ASC""",
        [task_id, session["user_id"]],
    ))


@tasks_bp.post("/api/comments")
@login_required
def create_comment():
    data = request.json
    task = get_one("""SELECT t.id FROM task t JOIN project p ON t.project_id = p.id
                      WHERE t.id = %s AND p.owner_id = %s""",
                   [data["task_id"], session["user_id"]])
    if not task:
        return jsonify({"error": "任务不存在"}), 404
    member_id = session.get("member_id") or data.get("member_id")
    if not member_id:
        return jsonify({"error": "请先关联团队成员身份"}), 400
    cid = execute(
        "INSERT INTO comment (task_id, member_id, content) VALUES (%s,%s,%s)",
        [data["task_id"], member_id, data["content"]],
    )
    log("发表了评论", "comment", cid, f"评论了任务#{data['task_id']}")
    return jsonify({"id": cid}), 201
