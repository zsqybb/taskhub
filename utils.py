"""共享工具函数"""
from db import get_one, execute


def opt_none(v):
    """将空字符串转为 None，用于 nullable 字段"""
    return None if v is None or (isinstance(v, str) and v.strip() == "") else v


def update_project_progress(project_id):
    """根据任务完成率更新 project.progress"""
    row = get_one(
        """SELECT COUNT(*) AS total, SUM(CASE WHEN status='done' THEN 1 ELSE 0 END) AS done
           FROM task WHERE project_id=%s""",
        [project_id],
    )
    if row and row["total"] > 0:
        progress = round(row["done"] / row["total"] * 100, 2)
    else:
        progress = 0.00
    execute("UPDATE project SET progress=%s WHERE id=%s", [progress, project_id])
