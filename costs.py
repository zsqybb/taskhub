"""成本管理蓝图"""
from flask import Blueprint, request, jsonify
from db import query, execute
from decorators import login_required
from activities import log
from utils import opt_none

costs_bp = Blueprint("costs", __name__)


@costs_bp.get("/api/costs")
@login_required
def list_costs():
    project_id = request.args.get("project_id")
    page = max(int(request.args.get("page", 1)), 1)
    per_page = min(max(int(request.args.get("per_page", 20)), 5), 100)
    offset = (page - 1) * per_page

    if project_id:
        sql = "SELECT * FROM cost WHERE project_id=%s ORDER BY cost_date DESC, id DESC LIMIT %s OFFSET %s"
        args = [project_id, per_page, offset]
        count_sql = "SELECT COUNT(*) AS total FROM cost WHERE project_id=%s"
        count_args = [project_id]
    else:
        sql = "SELECT * FROM cost ORDER BY cost_date DESC, id DESC LIMIT %s OFFSET %s"
        args = [per_page, offset]
        count_sql = "SELECT COUNT(*) AS total FROM cost"
        count_args = []

    rows = query(sql, args)
    total_row = query(count_sql, count_args)
    total = total_row[0]["total"] if total_row else 0

    return jsonify({"data": rows, "total": total, "page": page, "per_page": per_page})


@costs_bp.post("/api/costs")
@login_required
def create_cost():
    data = request.json
    cid = execute(
        "INSERT INTO cost (project_id, category, amount, description, cost_date) VALUES (%s,%s,%s,%s,%s)",
        [data["project_id"], data["category"], data["amount"], opt_none(data.get("description")), opt_none(data.get("cost_date"))],
    )
    log("记录了成本", "cost", cid, f"记录了成本 {data['amount']} 元")
    return jsonify({"id": cid}), 201


@costs_bp.delete("/api/costs/<int:cid>")
@login_required
def delete_cost(cid):
    execute("DELETE FROM cost WHERE id=%s", [cid])
    return jsonify({"ok": True})
