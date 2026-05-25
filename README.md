# TaskHub - 项目管理与任务协作平台

基于 Flask 的企业级项目管理工具，支持多用户数据隔离、项目跟踪、任务看板、工时记录、成本管理和数据导出。

## 功能概览

- **多用户隔离** — 注册即创建独立工作台，每个用户只能看到自己的项目和数据
- **项目管理** — 多项目进度追踪，里程碑规划，可视化统计看板
- **任务看板** — 任务 CRUD、优先级排序、四阶段状态流转
- **智能进度** — 按工时加权的项目进度计算（done 100% / review 75% / in_progress 50% / todo 0%）
- **团队协作** — 成员管理、任务分配、工时记录、评论讨论
- **个人中心** — 完善个人资料并自动同步到团队成员表
- **成本管理** — 按项目分类记录成本，自动汇总
- **数据看板** — 项目进度、任务状态分布、成本分类、成员工作量图表
- **活动日志** — 关键操作自动记录，支持按类型筛选
- **数据导出** — 支持 Excel (.xlsx) 导出项目、任务、成本

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | Flask 3.x |
| 数据库 | MySQL 8.x + PyMySQL + DBUtils 连接池 |
| 安全 | Session 认证、CSRF 保护、werkzeug scrypt 密码哈希 |
| 前端 | Chart.js 图表、原生 JS SSR 模板 |
| 导出 | openpyxl |

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

```sql
CREATE DATABASE task_hub CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

可选环境变量：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DB_HOST` | localhost | 数据库地址 |
| `DB_USER` | root | 数据库用户 |
| `DB_PASSWORD` | 123456 | 数据库密码 |
| `DB_NAME` | task_hub | 数据库名 |
| `SECRET_KEY` | 随机生成 | Flask 密钥 |
| `PORT` | 5000 | 监听端口 |
| `FLASK_DEBUG` | 0 | 调试模式 |

### 4. 启动

```bash
python app.py
```

浏览器访问 `http://127.0.0.1:5000`，使用管理员账号登录后，点击 **POST /api/init-db** 初始化数据库表和种子数据。

### 5. 默认账号

| 账号 | 密码 | 角色 |
|------|------|------|
| admin | 123456 | 管理员 |
| zhangwei | 123456 | 经理 |
| lina | 123456 | 经理 |
| wanglei | 123456 | 成员 |
| chenjing | 123456 | 成员 |

## 使用指南

### 项目工作流

```
创建项目 → 设置里程碑 → 创建任务 → 开始工作
                                     ↓
                              登记工时（worklog）
                                     ↓
                   todo → in_progress → review → done
                                             ↓
                                    看板自动更新进度
```

### 进度计算

按**工时加权 + 状态权重**，实时反映真实进度：

| 状态 | 权重 | 含义 |
|------|------|------|
| done | 100% | 已完成 |
| review | 75% | 评审中，基本完成 |
| in_progress | 50% | 进行中 |
| todo | 0% | 未开始 |

公式：`进度 = Σ(工时 × 状态权重) / Σ(工时) × 100%`

未填预估工时时回退为：`已完成数 / 总任务数`

### 数据隔离

每个注册用户自动获得独立工作台，拥有自己的团队成员档案。用户之间完全隔离，无法互相访问项目、任务、成本等数据。

## 项目结构

```
├── app.py              # 应用工厂、CSRF 中间件、数据库初始化
├── config.py           # 数据库与密钥配置
├── db.py               # 连接池 (PooledDB)、查询/写入/影响行数工具
├── utils.py            # 进度计算、参数校验等共享函数
├── decorators.py       # 认证装饰器 (login_required, admin_required)
├── auth.py             # 注册/登录/个人信息/修改密码/团队成员
├── dashboard.py        # 工作台统计 (合并查询)
├── projects.py         # 项目与里程碑 CRUD
├── tasks.py            # 任务 CRUD、工时记录、评论
├── costs.py            # 项目成本管理
├── activities.py       # 活动日志记录与查询
├── export.py           # Excel 数据导出 (项目/任务/成本)
├── schema.sql          # 完整建表语句 + 种子数据
├── requirements.txt    # Python 依赖
└── templates/
    ├── index.html      # 主控制台 (SPA)
    ├── login.html      # 登录页
    └── register.html   # 注册页
```

## API 概览

### 认证
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/login` | 登录 |
| POST | `/api/auth/register` | 注册（自动创建团队成员） |
| POST | `/api/auth/logout` | 登出 |
| GET | `/api/auth/me` | 当前用户信息（含团队成员详情） |
| PUT | `/api/auth/profile` | 更新个人资料（同步团队成员表） |
| PUT | `/api/auth/password` | 修改密码 |
| GET | `/api/auth/my-tasks` | 我的待办任务 |
| GET | `/api/auth/my-stats` | 我的工时统计 |

### 看板 & 团队
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/dashboard` | 工作台统计数据 |
| GET | `/api/members` | 团队成员列表（仅当前用户） |
| GET | `/api/activities` | 活动日志 |

### 项目管理
| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | `/api/projects` | 项目列表/创建 |
| GET/PUT/DELETE | `/api/projects/<id>` | 项目详情/更新/删除 |
| GET/POST | `/api/milestones` | 里程碑列表/创建 |

### 任务管理
| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | `/api/tasks` | 任务列表/创建 |
| GET/PUT/DELETE | `/api/tasks/<id>` | 任务详情/更新/删除 |
| GET/POST | `/api/worklogs` | 工时记录 |
| GET/POST | `/api/comments` | 任务评论 |

### 成本 & 导出
| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | `/api/costs` | 成本列表/记录 |
| DELETE | `/api/costs/<id>` | 删除成本记录 |
| GET | `/api/export/projects` | 导出项目 Excel |
| GET | `/api/export/tasks` | 导出任务 Excel |
| GET | `/api/export/costs` | 导出成本 Excel |

## 安全特性

- **多用户数据隔离** — 所有查询强制按 `owner_id` 过滤，跨用户访问返回 404
- **CSRF 保护** — 非 GET 请求需携带 `X-CSRF-Token` 头，初始登录时自动获取
- **Session 安全** — HttpOnly Cookie、SameSite=Lax、24h 过期
- **密码安全** — werkzeug scrypt 哈希，密码修改需验证原密码
- **输入校验** — 后端对所有必填字段进行校验，返回明确错误信息
- **邮箱唯一性** — 修改邮箱时自动检查 team_member 和 user 表冲突
- **连接池管理** — DBUtils PooledDB 防止连接泄漏
