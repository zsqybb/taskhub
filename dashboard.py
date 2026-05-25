"""工作台蓝图 — 统计 + 图表数据 + 活动日志"""
from flask import Blueprint, jsonify
from db import query, get_one
from decorators import login_required

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("/api/dashboard")
@login_required
def dashboard():
    # 1. 项目统计 + 进度图表 (合并 4 条查询)
    project_rows = query("""
        SELECT p.id, p.name, p.progress, p.status,
               COUNT(t.id) AS task_count,
               SUM(CASE WHEN t.status='done' THEN 1 ELSE 0 END) AS done_count
        FROM project p
        LEFT JOIN task t ON t.project_id = p.id
        GROUP BY p.id ORDER BY p.progress DESC
    """)
    total_projects = len(project_rows)
    active_projects = sum(1 for r in project_rows if r["status"] == "in_progress")
    project_progress = project_rows[:5]
    project_chart = [{"name": r["name"], "progress": r["progress"]} for r in project_rows]

    # 2. 任务统计 + 状态分布 (合并 3 条查询)
    task_status_rows = query("SELECT status, COUNT(*) AS count FROM task GROUP BY status")
    status_map = {r["status"]: r["count"] for r in task_status_rows}
    total_tasks = sum(status_map.values())
    done_tasks = status_map.get("done", 0)
    task_status_chart = task_status_rows

    # 3. 成本统计 + 分类 (合并 2 条查询)
    cost_rows = query("SELECT category, SUM(amount) AS total FROM cost GROUP BY category ORDER BY total DESC")
    total_cost = sum(r["total"] for r in cost_rows) if cost_rows else 0
    cost_category_chart = cost_rows

    # 4. 团队成员数
    total_members = get_one("SELECT COUNT(*) AS c FROM team_member WHERE status=1")["c"]

    # 5. 成员工作量排行
    workload = query("""
        SELECT tm.name, COUNT(t.id) AS task_count
        FROM team_member tm
        LEFT JOIN task t ON t.assignee_id = tm.id AND t.status != 'done'
        WHERE tm.status = 1 GROUP BY tm.id, tm.name
        ORDER BY task_count DESC LIMIT 5
    """)

    return jsonify({
        "total_projects": total_projects, "active_projects": active_projects,
        "total_tasks": total_tasks, "done_tasks": done_tasks,
        "total_members": total_members, "total_cost": total_cost,
        "project_progress": project_progress, "workload": workload,
        "task_status_chart": task_status_chart,
        "cost_category_chart": cost_category_chart,
        "project_chart": project_chart,
    })
