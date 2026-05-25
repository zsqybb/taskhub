"""共享工具函数"""
from db import get_one, execute, query


def opt_none(v):
    """将空字符串转为 None，用于 nullable 字段"""
    return None if v is None or (isinstance(v, str) and v.strip() == "") else v


def parse_int(val, default, min_val=None, max_val=None):
    """安全解析整数，失败时返回默认值"""
    try:
        v = int(val)
    except (ValueError, TypeError):
        return default
    if min_val is not None and v < min_val:
        return min_val
    if max_val is not None and v > max_val:
        return max_val
    return v


def update_project_progress(project_id):
    """按任务状态加权计算进度（有预估工时则按时数加权）"""
    tasks = query(
        """SELECT status, estimated_hours FROM task WHERE project_id=%s""",
        [project_id],
    )
    if not tasks:
        execute("UPDATE project SET progress=%s WHERE id=%s", [0.00, project_id])
        return

    STATUS_WEIGHT = {"done": 1.0, "review": 0.75, "in_progress": 0.5, "todo": 0.0}
    has_hours = any(t["estimated_hours"] is not None for t in tasks)

    if has_hours:
        total_weight = 0.0
        earned_weight = 0.0
        for t in tasks:
            h = float(t["estimated_hours"] or 0)
            w = STATUS_WEIGHT.get(t["status"], 0)
            total_weight += h
            earned_weight += h * w
        progress = round(earned_weight / total_weight * 100, 2) if total_weight > 0 else 0.0
    else:
        done_count = sum(1 for t in tasks if t["status"] == "done")
        progress = round(done_count / len(tasks) * 100, 2)

    execute("UPDATE project SET progress=%s WHERE id=%s", [progress, project_id])
