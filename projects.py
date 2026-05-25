"""项目与里程碑蓝图"""
from flask import Blueprint, request, jsonify
from db import query, get_one, execute
from decorators import login_required
from activities import log
from utils import opt_none, update_project_progress

projects_bp = Blueprint("projects", __name__)


# ── 项目 CRUD ──────────────────────────────────────
@projects_bp.get("/api/projects")
@login_required
def list_projects():
    search = request.args.get("search", "").strip()
    page = max(int(request.args.get("page", 1)), 1)
    per_page = min(max(int(request.args.get("per_page", 20)), 5), 100)
    offset = (page - 1) * per_page

    sql = """
        SELECT p.*, tm.name AS manager_name,
               COUNT(t.id) AS task_count,
               SUM(CASE WHEN t.status='done' THEN 1 ELSE 0 END) AS done_count
        FROM project p
        LEFT JOIN team_member tm ON p.manager_id = tm.id
        LEFT JOIN task t ON t.project_id = p.id
    """
    count_sql = "SELECT COUNT(*) AS total FROM project p"
    args = []
    count_args = []

    if search:
        sql += " WHERE p.name LIKE %s"
        count_sql += " WHERE p.name LIKE %s"
        like_val = f"%{search}%"
        args.append(like_val)
        count_args.append(like_val)

    sql += " GROUP BY p.id ORDER BY p.created_at DESC LIMIT %s OFFSET %s"
    args += [per_page, offset]

    rows = query(sql, args)
    total = get_one(count_sql, count_args)["total"] if count_args else get_one("SELECT COUNT(*) AS total FROM project")["total"]

    return jsonify({"data": rows, "total": total, "page": page, "per_page": per_page})


@projects_bp.get("/api/projects/<int:pid>")
@login_required
def get_project(pid):
    row = get_one(
        """SELECT p.*, tm.name AS manager_name
           FROM project p LEFT JOIN team_member tm ON p.manager_id = tm.id
           WHERE p.id = %s""",
        [pid],
    )
    if not row:
        return jsonify({"error": "项目不存在"}), 404
    return jsonify(row)


@projects_bp.post("/api/projects")
@login_required
def create_project():
    data = request.json
    pid = execute(
        """INSERT INTO project (name, description, status, priority, budget, start_date, end_date, manager_id)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
        [data["name"], opt_none(data.get("description")), data.get("status", "planning"),
         data.get("priority", 2), data.get("budget", 0), opt_none(data.get("start_date")),
         opt_none(data.get("end_date")), opt_none(data.get("manager_id"))],
    )
    log("创建了项目", "project", pid, f"创建了项目「{data['name']}」")
    return jsonify({"id": pid}), 201


@projects_bp.put("/api/projects/<int:pid>")
@login_required
def update_project(pid):
    data = request.json
    execute(
        """UPDATE project SET name=%s, description=%s, status=%s, priority=%s,
           budget=%s, start_date=%s, end_date=%s, manager_id=%s WHERE id=%s""",
        [data["name"], opt_none(data.get("description")), data.get("status"), data.get("priority"),
         data.get("budget"), opt_none(data.get("start_date")), opt_none(data.get("end_date")),
         opt_none(data.get("manager_id")), pid],
    )
    log("更新了项目", "project", pid, f"更新了项目「{data['name']}」")
    return jsonify({"ok": True})


@projects_bp.delete("/api/projects/<int:pid>")
@login_required
def delete_project(pid):
    p = get_one("SELECT name FROM project WHERE id=%s", [pid])
    execute("DELETE FROM project WHERE id=%s", [pid])
    if p:
        log("删除了项目", "project", pid, f"删除了项目「{p['name']}」")
    return jsonify({"ok": True})


# ── 里程碑 ─────────────────────────────────────────
@projects_bp.get("/api/milestones")
@login_required
def list_milestones():
    project_id = request.args.get("project_id")
    if project_id:
        return jsonify(query(
            "SELECT * FROM milestone WHERE project_id=%s ORDER BY sort_order, id",
            [project_id],
        ))
    return jsonify(query("SELECT * FROM milestone ORDER BY sort_order, id"))


@projects_bp.post("/api/milestones")
@login_required
def create_milestone():
    data = request.json
    mid = execute(
        """INSERT INTO milestone (project_id, name, description, due_date, status, sort_order)
           VALUES (%s,%s,%s,%s,%s,%s)""",
        [data["project_id"], data["name"], data.get("description"), data.get("due_date"),
         data.get("status", "pending"), data.get("sort_order", 0)],
    )
    return jsonify({"id": mid}), 201
