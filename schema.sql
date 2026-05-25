-- TaskHub - 项目管理与任务协作平台
-- Database Schema

CREATE DATABASE IF NOT EXISTS task_hub CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE task_hub;

-- ============================================================
-- 用户认证表
-- ============================================================
CREATE TABLE user (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    display_name VARCHAR(50),
    role ENUM('admin','manager','member') NOT NULL DEFAULT 'member',
    status TINYINT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================
-- 团队成员表
-- ============================================================
CREATE TABLE team_member (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    role ENUM('admin','manager','member') NOT NULL DEFAULT 'member',
    department VARCHAR(50),
    avatar_url VARCHAR(255),
    user_id INT,
    status TINYINT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ============================================================
-- 项目表
-- ============================================================
CREATE TABLE project (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    owner_id INT NOT NULL,
    status ENUM('planning','in_progress','completed','cancelled') NOT NULL DEFAULT 'planning',
    priority TINYINT DEFAULT 2,
    budget DECIMAL(12,2) DEFAULT 0.00,
    start_date DATE,
    end_date DATE,
    manager_id INT,
    progress DECIMAL(5,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (manager_id) REFERENCES team_member(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ============================================================
-- 里程碑表
-- ============================================================
CREATE TABLE milestone (
    id INT PRIMARY KEY AUTO_INCREMENT,
    project_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    due_date DATE,
    status ENUM('pending','in_progress','completed') NOT NULL DEFAULT 'pending',
    sort_order INT DEFAULT 0,
    completed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES project(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- 任务表
-- ============================================================
CREATE TABLE task (
    id INT PRIMARY KEY AUTO_INCREMENT,
    project_id INT NOT NULL,
    milestone_id INT,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status ENUM('todo','in_progress','review','done') NOT NULL DEFAULT 'todo',
    priority TINYINT DEFAULT 2,
    assignee_id INT,
    estimated_hours DECIMAL(5,1) DEFAULT NULL,
    actual_hours DECIMAL(5,1) DEFAULT 0.0,
    parent_task_id INT DEFAULT NULL,
    sort_order INT DEFAULT 0,
    start_date DATE,
    due_date DATE,
    completed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES project(id) ON DELETE CASCADE,
    FOREIGN KEY (milestone_id) REFERENCES milestone(id) ON DELETE SET NULL,
    FOREIGN KEY (assignee_id) REFERENCES team_member(id) ON DELETE SET NULL,
    FOREIGN KEY (parent_task_id) REFERENCES task(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ============================================================
-- 工时记录表
-- ============================================================
CREATE TABLE work_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    task_id INT NOT NULL,
    member_id INT NOT NULL,
    hours DECIMAL(4,1) NOT NULL,
    log_date DATE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES task(id) ON DELETE CASCADE,
    FOREIGN KEY (member_id) REFERENCES team_member(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- 项目成本表
-- ============================================================
CREATE TABLE cost (
    id INT PRIMARY KEY AUTO_INCREMENT,
    project_id INT NOT NULL,
    category VARCHAR(50) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    description VARCHAR(255),
    cost_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES project(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- 任务评论表
-- ============================================================
CREATE TABLE comment (
    id INT PRIMARY KEY AUTO_INCREMENT,
    task_id INT NOT NULL,
    member_id INT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES task(id) ON DELETE CASCADE,
    FOREIGN KEY (member_id) REFERENCES team_member(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- 活动日志表
-- ============================================================
CREATE TABLE activity_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    member_id INT,
    username VARCHAR(50),
    action VARCHAR(50) NOT NULL,
    target_type VARCHAR(30),
    target_id INT,
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================
-- 种子数据
-- ============================================================

-- 用户 (密码均为 123456)
INSERT INTO user (username, email, password_hash, display_name, role) VALUES
('admin',     'admin@taskhub.com',      'scrypt:32768:8:1$xLdkcTnj8gya1pzU$bf1145154be581faa131e21f5fac63b1aae87ab0885a46806255a06bcabf6577f412fd4edc68333c44a729f2b4bc4153898069a9c1b132929e8c483a5110cd8f', '系统管理员', 'admin'),
('zhangwei',  'zhangwei@taskhub.com',   'scrypt:32768:8:1$xLdkcTnj8gya1pzU$bf1145154be581faa131e21f5fac63b1aae87ab0885a46806255a06bcabf6577f412fd4edc68333c44a729f2b4bc4153898069a9c1b132929e8c483a5110cd8f', '张伟',       'manager'),
('lina',      'lina@taskhub.com',       'scrypt:32768:8:1$xLdkcTnj8gya1pzU$bf1145154be581faa131e21f5fac63b1aae87ab0885a46806255a06bcabf6577f412fd4edc68333c44a729f2b4bc4153898069a9c1b132929e8c483a5110cd8f', '李娜',       'manager'),
('wanglei',   'wanglei@taskhub.com',    'scrypt:32768:8:1$xLdkcTnj8gya1pzU$bf1145154be581faa131e21f5fac63b1aae87ab0885a46806255a06bcabf6577f412fd4edc68333c44a729f2b4bc4153898069a9c1b132929e8c483a5110cd8f', '王磊',       'member'),
('chenjing',  'chenjing@taskhub.com',   'scrypt:32768:8:1$xLdkcTnj8gya1pzU$bf1145154be581faa131e21f5fac63b1aae87ab0885a46806255a06bcabf6577f412fd4edc68333c44a729f2b4bc4153898069a9c1b132929e8c483a5110cd8f', '陈静',       'member');

-- 团队成员
INSERT INTO team_member (id, name, email, phone, role, department, user_id) VALUES
(1, '张伟',   'zhangwei@company.com',   '13800001111', 'admin',   '技术部', 2),
(2, '李娜',   'lina@company.com',       '13800002222', 'manager', '产品部', 3),
(3, '王磊',   'wanglei@company.com',    '13800003333', 'member',  '前端组', 4),
(4, '陈静',   'chenjing@company.com',   '13800004444', 'member',  '后端组', 5),
(5, '刘洋',   'liuyang@company.com',    '13800005555', 'member',  '测试组', NULL),
(6, '赵敏',   'zhaomin@company.com',    '13800006666', 'member',  '设计组', NULL),
(7, '孙鹏',   'sunpeng@company.com',    '13800007777', 'manager', '运维部', NULL),
(8, '周婷',   'zhouting@company.com',   '13800008888', 'member',  '后端组', NULL);

-- 项目
INSERT INTO project (id, name, description, owner_id, status, priority, budget, start_date, end_date, manager_id, progress) VALUES
(1, '智能CRM系统',   '企业客户关系管理系统，包含客户管理、销售漏斗、数据分析', 1, 'in_progress', 4, 500000.00, '2026-03-01', '2026-08-31', 2, 45.00),
(2, '数据中台建设',   '统一数据资产管理平台，整合各部门数据源',              1, 'in_progress', 3, 800000.00, '2026-04-01', '2026-10-31', 7, 20.00),
(3, '移动办公App',    '企业移动办公平台 iOS/Android 双端',                  1, 'planning',    3, 350000.00, '2026-06-01', '2026-12-31', 2,  0.00),
(4, '运维监控平台',   '服务器与微服务实时监控告警系统',                      1, 'planning',    2, 200000.00, '2026-07-01', '2027-01-31', 7,  0.00),
(5, '内部知识库',     '团队知识沉淀与分享平台',                              1, 'completed',   1,  80000.00, '2026-01-01', '2026-04-30', 2, 100.00);

-- 里程碑（智能CRM系统）
INSERT INTO milestone (id, project_id, name, due_date, status, sort_order) VALUES
(1, 1, '需求调研完成', '2026-03-31', 'completed',   1),
(2, 1, '原型设计评审', '2026-04-30', 'completed',   2),
(3, 1, '核心模块开发', '2026-06-30', 'in_progress', 3),
(4, 1, '系统测试上线', '2026-08-15', 'pending',     4);

-- 里程碑（数据中台建设）
INSERT INTO milestone (id, project_id, name, due_date, status, sort_order) VALUES
(5, 2, '技术选型确认', '2026-04-30', 'completed',   1),
(6, 2, '数据接入层开发','2026-07-31', 'in_progress', 2),
(7, 2, '数据服务层开发','2026-09-30', 'pending',     3);

-- 任务（智能CRM系统）
INSERT INTO task (id, project_id, milestone_id, title, status, priority, assignee_id, estimated_hours, actual_hours, sort_order) VALUES
(1, 1, 3, '客户列表页 CRUD',           'done',        4, 3, 16, 14, 1),
(2, 1, 3, '客户分页与搜索筛选',        'review',      3, 4,  8,  6, 2),
(3, 1, 3, '销售漏斗可视化图表',         'in_progress', 4, 3, 24, 10, 3),
(4, 1, 3, '合同管理模块',              'todo',        3, 3, 20,  0, 4),
(5, 1, 3, '数据导出 Excel/PDF',        'todo',        2, 8, 12,  0, 5),
(6, 1, 4, '权限与角色管理',            'todo',        3, 4, 16,  0, 6),
(7, 1, 4, '操作日志审计',              'todo',        2, 4,  8,  0, 7);

-- 任务（数据中台建设）
INSERT INTO task (id, project_id, milestone_id, title, status, priority, assignee_id, estimated_hours, actual_hours, sort_order) VALUES
(8,  2, 6, '数据源连接器开发 (MySQL)',      'done',        3, 4, 20, 18, 1),
(9,  2, 6, '数据源连接器开发 (ES)',          'in_progress', 3, 4, 16,  8, 2),
(10, 2, 6, '实时数据同步管道',               'todo',        4, 7, 32,  0, 3),
(11, 2, 6, '数据质量校验引擎',               'todo',        3, 8, 20,  0, 4),
(12, 2, 7, '统一查询API网关',                'todo',        3, 4, 24,  0, 5);

-- 工时记录
INSERT INTO work_log (task_id, member_id, hours, log_date, description) VALUES
(1, 3, 6, '2026-05-12', '完成客户列表页基本布局和 API 对接'),
(1, 3, 4, '2026-05-13', '完成新增/编辑/删除功能'),
(1, 4, 4, '2026-05-14', '后端 CRUD 接口联调'),
(3, 3, 4, '2026-05-20', 'ECharts 图表组件集成'),
(3, 4, 6, '2026-05-21', '销售漏斗数据聚合查询优化'),
(8, 4, 8, '2026-05-15', 'MySQL CDC 连接器核心逻辑'),
(8, 4, 6, '2026-05-16', '数据映射与转换层'),
(8, 8, 4, '2026-05-17', '连接器单元测试'),
(9, 4, 8, '2026-05-19', 'ES 索引映射与全量同步');

-- 项目成本
INSERT INTO cost (project_id, category, amount, description, cost_date) VALUES
(1, 'software',   25000.00, '设计工具授权 (Figma/Sketch)', '2026-03-15'),
(1, 'labor',      80000.00, '3-5月研发人力成本',           '2026-05-01'),
(1, 'equipment',  15000.00, '测试服务器购置',              '2026-04-10'),
(1, 'travel',      5000.00, '客户现场需求调研差旅',        '2026-03-20'),
(2, 'software',   40000.00, '中间件授权 (Kafka/ES)',       '2026-04-15'),
(2, 'labor',      60000.00, '4-5月研发人力成本',           '2026-05-01'),
(2, 'equipment',  30000.00, '数据集群服务器',              '2026-04-20');

-- 评论
INSERT INTO comment (task_id, member_id, content) VALUES
(2, 2, '分页组件需要支持每页 10/20/50 条切换'),
(2, 3, '已加上，另外增加了按客户等级筛选'),
(3, 2, '漏斗图能不能显示各阶段的转化率百分比？'),
(3, 3, '好的，我在图表上加上百分比标签'),
(9, 7, 'ES 连接器需要支持 7.x 和 8.x 两个大版本');
