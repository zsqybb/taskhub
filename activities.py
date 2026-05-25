"""活动日志 — 记录关键操作并查询"""
import logging
from flask import Blueprint, request, jsonify, session
from db import execute, query
from decorators import login_required

activities_bp = Blueprint("activities", __name__)
_logger = logging.getLogger("taskhub")


def log(action, target_type, target_id, description=""):
    """记录一条活动日志（供其他模块调用）"""
    user_id = session.get("user_id")
    username = session.get("username", "system")
    member_id = session.get("member_id")
    if not description:
        display = session.get("display_name") or username
        description = f"{display} {action}"
    try:
        execute(
            "INSERT INTO activity_log (user_id, member_id, username, action, target_type, target_id, description) VALUES (%s,%s,%s,%s,%s,%s,%s)",
            [user_id, member_id, username, action, target_type, target_id, description],
        )
    except Exception as e:
        _logger.warning("Activity log insert failed: %s", e)


@activities_bp.get("/api/activities")
@login_required
def list_activities():
    limit = int(request.args.get("limit", 20))
    target_type = request.args.get("type", "").strip()
    project_id = request.args.get("project_id", "").strip()

    sql = "SELECT * FROM activity_log"
    conditions = []
    args = []

    if target_type:
        conditions.append("target_type = %s")
        args.append(target_type)
    if project_id:
        conditions.append("target_type = 'project'")
        conditions.append("target_id = %s")
        args.append(project_id)

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    sql += " ORDER BY created_at DESC LIMIT %s"
    args.append(limit)

    return jsonify(query(sql, args))
