"""成本管理蓝图"""
from flask import Blueprint, request, jsonify, session
from db import query, get_one, execute, execute_affected
from decorators import login_required
from activities import log
from utils import opt_none, parse_int

costs_bp = Blueprint("costs", __name__)


@costs_bp.get("/api/costs")
@login_required
def list_costs():
    project_id = request.args.get("project_id")
    page = parse_int(request.args.get("page", 1), 1)
    per_page = parse_int(request.args.get("per_page", 20), 20, 5, 100)
    offset = (page - 1) * per_page

    if project_id:
        sql = """SELECT c.* FROM cost c JOIN project p ON c.project_id = p.id
                 WHERE p.id = %s AND p.owner_id = %s
                 ORDER BY c.cost_date DESC, c.id DESC LIMIT %s OFFSET %s"""
        args = [project_id, session["user_id"], per_page, offset]
        count_sql = """SELECT COUNT(*) AS total FROM cost c JOIN project p ON c.project_id = p.id
                       WHERE p.id = %s AND p.owner_id = %s"""
        count_args = [project_id, session["user_id"]]
    else:
        sql = """SELECT c.* FROM cost c JOIN project p ON c.project_id = p.id
                 WHERE p.owner_id = %s
                 ORDER BY c.cost_date DESC, c.id DESC LIMIT %s OFFSET %s"""
        args = [session["user_id"], per_page, offset]
        count_sql = """SELECT COUNT(*) AS total FROM cost c JOIN project p ON c.project_id = p.id
                       WHERE p.owner_id = %s"""
        count_args = [session["user_id"]]

    rows = query(sql, args)
    total_row = query(count_sql, count_args)
    total = total_row[0]["total"] if total_row else 0

    return jsonify({"data": rows, "total": total, "page": page, "per_page": per_page})


@costs_bp.post("/api/costs")
@login_required
def create_cost():
    data = request.json
    project_id = data.get("project_id")
    category = (data.get("category") or "").strip()
    amount = data.get("amount")
    if not project_id:
        return jsonify({"error": "请指定所属项目"}), 400
    if not category:
        return jsonify({"error": "请选择成本类别"}), 400
    if amount is None or (isinstance(amount, (int, float)) and amount <= 0):
        return jsonify({"error": "金额必须大于0"}), 400
    proj = get_one("SELECT id FROM project WHERE id=%s AND owner_id=%s",
                   [project_id, session["user_id"]])
    if not proj:
        return jsonify({"error": "项目不存在"}), 404
    cid = execute(
        "INSERT INTO cost (project_id, category, amount, description, cost_date) VALUES (%s,%s,%s,%s,%s)",
        [project_id, category, amount, opt_none(data.get("description")), opt_none(data.get("cost_date"))],
    )
    log("记录了成本", "cost", cid, f"记录了成本 {amount} 元")
    return jsonify({"id": cid}), 201


@costs_bp.delete("/api/costs/<int:cid>")
@login_required
def delete_cost(cid):
    affected = execute_affected(
        """DELETE c FROM cost c JOIN project p ON c.project_id = p.id
           WHERE c.id = %s AND p.owner_id = %s""",
        [cid, session["user_id"]],
    )
    if not affected:
        return jsonify({"error": "成本记录不存在"}), 404
    return jsonify({"ok": True})
