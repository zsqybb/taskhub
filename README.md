# TaskHub - 项目管理与任务协作平台

基于 Flask 的企业级项目管理工具，支持项目跟踪、任务分配、工时记录、成本管理和数据导出。

## 功能概览

- **项目管理** — 多项目进度追踪，里程碑规划，可视化统计看板
- **任务管理** — 任务 CRUD、优先级排序、状态流转（todo → in_progress → review → done）
- **团队协作** — 成员管理、任务分配、工时记录、评论讨论
- **成本管理** — 按项目分类记录成本，自动汇总
- **数据看板** — 项目进度、任务状态分布、成本分类图表
- **活动日志** — 关键操作自动记录，支持按类型筛选
- **数据导出** — 支持 Excel 导出

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | Flask 3.x |
| 数据库 | MySQL 8.x + PyMySQL + DBUtils 连接池 |
| 安全 | Session 认证、CSRF 保护、werkzeug 密码哈希 |
| 前端 | ECharts 图表、原生 JS (SSR 模板渲染) |

## 快速开始

### 1. 环境要求

- Python 3.10+
- MySQL 8.0+
- pip

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置数据库

创建数据库：

```sql
CREATE DATABASE task_hub CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

可选：通过环境变量覆盖默认配置

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DB_HOST` | localhost | 数据库地址 |
| `DB_USER` | root | 数据库用户 |
| `DB_PASSWORD` | 123456 | 数据库密码 |
| `DB_NAME` | task_hub | 数据库名 |
| `SECRET_KEY` | 随机生成 | Flask 密钥 |
| `PORT` | 5000 | 监听端口 |
| `FLASK_DEBUG` | 0 | 调试模式 |

### 4. 初始化数据库并启动

```bash
# 启动应用
python app.py

# 访问 http://127.0.0.1:5000
# 使用管理员登录后，访问 /api/init-db (POST) 初始化表结构和种子数据
```

### 5. 默认账号

| 账号 | 密码 | 角色 |
|------|------|------|
| admin | 123456 | 管理员 |
| zhangwei | 123456 | 经理 |
| lina | 123456 | 经理 |
| wanglei | 123456 | 成员 |
| chenjing | 123456 | 成员 |

## 项目结构

```
claude-first/
├── app.py              # 应用工厂、路由注册、CSRF 中间件
├── config.py           # 数据库与密钥配置
├── db.py               # 连接池 (PooledDB)、查询/写入工具
├── utils.py            # 共享工具函数
├── decorators.py       # 认证装饰器 (login_required, admin_required)
├── auth.py             # 注册/登录/个人信息/团队成员
├── dashboard.py        # 工作台统计 (5条合并查询)
├── projects.py         # 项目与里程碑 CRUD
├── tasks.py            # 任务 CRUD、工时记录、评论
├── costs.py            # 项目成本管理
├── activities.py       # 活动日志记录与查询
├── export.py           # Excel 数据导出
├── schema.sql          # 完整建表语句 + 种子数据
├── requirements.txt    # Python 依赖
├── templates/
│   ├── index.html      # 主控制台
│   ├── login.html      # 登录页
│   └── register.html   # 注册页
└── static/
    └── ...
```

## API 概览

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/login` | 登录 |
| POST | `/api/auth/register` | 注册 |
| GET | `/api/auth/me` | 当前用户信息 |
| GET | `/api/dashboard` | 工作台统计数据 |
| GET/POST | `/api/projects` | 项目列表/创建 |
| PUT/DELETE | `/api/projects/<id>` | 项目更新/删除 |
| GET/POST | `/api/tasks` | 任务列表/创建 |
| PUT/DELETE | `/api/tasks/<id>` | 任务更新/删除 |
| GET | `/api/milestones` | 里程碑列表 |
| GET/POST | `/api/worklogs` | 工时记录 |
| GET/POST | `/api/comments` | 任务评论 |
| GET/POST | `/api/costs` | 成本管理 |
| GET | `/api/activities` | 活动日志 |
| GET | `/api/export/*` | 数据导出 |

## 安全特性

- Session Cookie 配置 (HttpOnly / SameSite=Lax)
- CSRF Token 双重验证 (非 GET 请求需携带 `X-CSRF-Token` 头)
- werkzeug scrypt 密码哈希
- 数据库连接池防止连接泄漏
- 敏感配置通过环境变量注入
