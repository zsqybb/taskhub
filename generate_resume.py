"""生成包含 TaskHub 项目的新简历 PDF"""
from fpdf import FPDF

class ResumePDF(FPDF):
    def __init__(self):
        super().__init__('P', 'mm', 'A4')
        self.set_auto_page_break(True, 15)
        # 注册字体
        self.add_font('MSYH', '', r'C:\Windows\Fonts\msyh.ttc', uni=True)
        self.add_font('MSYH', 'B', r'C:\Windows\Fonts\msyhbd.ttc', uni=True)
        self.add_font('HEI', '', r'C:\Windows\Fonts\simhei.ttf', uni=True)
        self.cjk_font = 'MSYH'
        self.bold_font = 'MSYH'
        self.title_font = 'HEI'

    def section_title(self, title, y=None):
        if y: self.set_y(y)
        self.set_fill_color(99, 102, 241)  # 紫色背景
        self.set_text_color(255, 255, 255)
        self.set_font(self.title_font, '', 11)
        self.cell(0, 7, f'  {title}', ln=True, fill=True)
        self.set_text_color(51, 51, 51)
        self.ln(3)

    def sub_title(self, text):
        self.set_font(self.cjk_font, 'B', 10.5)
        self.set_text_color(99, 102, 241)
        self.cell(0, 6, text, ln=True)
        self.set_text_color(51, 51, 51)

    def body_text(self, text, indent=4):
        self.set_font(self.cjk_font, '', 9.5)
        self.set_x(self.l_margin + indent)
        self.multi_cell(190 - indent, 5.5, text)

    def bullet(self, text, indent=6):
        self.set_font(self.cjk_font, '', 9)
        self.set_x(self.l_margin + indent)
        self.cell(4, 5, '•')
        self.multi_cell(186 - indent, 5, text)

    def skill_row(self, label, content):
        self.set_font(self.cjk_font, 'B', 9.5)
        self.cell(22, 6, label)
        self.set_font(self.cjk_font, '', 9)
        self.multi_cell(168, 6, content)


def build():
    pdf = ResumePDF()
    pdf.l_margin = 20
    pdf.r_margin = 20

    # ═══════════════ PAGE 1 ═══════════════
    pdf.add_page()

    # ── Header ──
    pdf.set_font(pdf.title_font, '', 22)
    pdf.set_text_color(99, 102, 241)
    pdf.cell(0, 10, '张帅谦', ln=True)
    pdf.set_font(pdf.cjk_font, '', 9)
    pdf.set_text_color(100, 100, 100)

    # Contact line
    pdf.cell(0, 5.5, '电话 19061622018  |  邮箱 575169919@qq.com  |  地址 河北省保定市', ln=True)
    pdf.cell(0, 5.5, '学校 保定理工学院 · 人工智能专业 · 本科 (2023.09 – 2027.06)  |  GitHub github.com/zsqybb', ln=True)
    pdf.ln(2)

    # ── 求职意向 ──
    pdf.set_font(pdf.cjk_font, 'B', 10)
    pdf.set_text_color(99, 102, 241)
    pdf.cell(0, 6, '求职意向：AI Agent 开发 / 大模型应用开发 / Python 实习（2027届，可尽快到岗）', ln=True)
    pdf.ln(3)

    # ── AI 项目实战 ──
    pdf.section_title('AI 项目实战')
    pdf.body_text('熟练使用 AI Agent 框架进行实时协作开发、全栈项目构建与智能对话系统搭建。日常使用 Claude Code / Cursor / Trae 进行 AI 辅助编程，使用 Dify / Coze 搭建 RAG 问答与图像识别工作流。')

    # ── 项目经历 ──
    pdf.section_title('项目经历')

    # Project 1: AI Agent
    pdf.sub_title('AI Agent 基础设施研究 | A2A + MCP + ReAct')
    pdf.bullet('基于 Google A2A 协议实现多 Agent 通信系统，支持搜索/机票 Agent 间协作调度')
    pdf.bullet('基于 MCP Server/Client 架构，使用 FastMCP + stdio transport 实现标准化工具调用')
    pdf.bullet('实现 ReAct 模式 Agent（Thought → Action → Observation 循环），支持自定义工具注册与调度')
    pdf.ln(1)

    # Project 2: English AI Assistant
    pdf.sub_title('英语学习 AI 助手 | Python + Flask + 腾讯智慧 API + Railway')
    pdf.bullet('构建 SkillDispatcher 路由层，实现单词查询/语法纠错/作文批改/通用问答 4 条处理链路')
    pdf.bullet('OCR 图像识别准确率 90%+，部署于 Railway 云平台稳定运行')
    pdf.ln(1)

    # Project 3: TaskHub ← NEW
    pdf.sub_title('TaskHub — 企业级项目管理协作平台 | Python + Flask + MySQL + Docker + Nginx')
    pdf.bullet('独立设计多租户数据隔离架构，所有 API 通过 owner_id 外键级联过滤，注册即创建独立工作台')
    pdf.bullet('设计工时加权进度算法：根据任务状态（done/review/in_progress/todo）和预估工时动态计算项目进度')
    pdf.bullet('实现 CSRF Token 验证 + Session 安全加固（HttpOnly/SameSite），输入校验防 500 错误')
    pdf.bullet('构建 16 个 RESTful API 端点（认证/看板/项目/任务/成本/导出），前端 Chart.js 可视化看板')
    pdf.bullet('编写 Docker + Gunicorn + Nginx 生产部署配置，部署至 PythonAnywhere 云端')
    pdf.ln(1)

    # Project 4: Cross-border Logistics
    pdf.sub_title('跨境物流方案问答系统 | Dify + RAG + Docker + Embedding')
    pdf.bullet('使用 Docker 部署 Dify 平台，搭建 RAG 知识增强 + OCR 图像识别问答流程')
    pdf.bullet('实现多轮对话上下文管理、答案质量验证与多级数据清洗，完成全流程测试')
    pdf.ln(1)

    # Project 5: Legal Case Classification
    pdf.sub_title('法律案件智能分类系统 | Python + Scikit-learn + Jieba + Pandas')
    pdf.bullet('基于 TF-IDF 特征提取 + 多模型对比（朴素贝叶斯/SVM/逻辑回归），实现法律案件自动分类')
    pdf.bullet('完成数据预处理、特征工程、模型评估全流程，输出准确率/召回率/F1 指标报告')
    pdf.ln(1)

    # Project 6: YOLOv8
    pdf.sub_title('YOLOv8 目标检测系统 | YOLOv8 + OpenCV + Python')
    pdf.bullet('完成数据集标注（500+ 张）、模型训练、超参数调优，mAP@0.5 达 85%+，推理速度 30+ FPS')
    pdf.ln(1)

    # Project 7: Sentiment Analysis
    pdf.sub_title('中文情感分析 | PaddleNLP + PyTorch + HuggingFace Transformers')
    pdf.bullet('实现多模型中文情感分类对比，涵盖深度学习预训练模型、规则匹配、统计分析方法')
    pdf.bullet('完成法律文书/社交媒体文本的多分类任务，含完整数据预处理与模型优化')

    # ═══════════════ PAGE 2 ═══════════════
    pdf.add_page()

    # ── 专业技能 ──
    pdf.section_title('专业技能')

    pdf.set_font(pdf.cjk_font, '', 9.5)
    skills = [
        ('编程语言', 'Python（熟练）、C++、Java、JavaScript'),
        ('AI 框架', 'PyTorch · HuggingFace · PaddleNLP · Scikit-learn'),
        ('NLP', 'RAG · LangChain · Embedding · OCR 识别 · 情感分析 · 文本分类'),
        ('Agent 架构', 'ReAct · A2A · MCP · Function Calling · Skill Dispatch'),
        ('AI 工具', 'OpenClaw · Claude Code · Cursor · Trae · Dify · Coze'),
        ('计算机视觉', 'YOLOv8 · OpenCV · Stable Diffusion'),
        ('后端/全栈', 'Flask · MySQL · Docker · Git · Linux · Nginx · Railway'),
    ]
    for label, content in skills:
        pdf.skill_row(label, content)
    pdf.ln(4)

    # ── 个人总结 ──
    pdf.section_title('个人总结')

    summaries = [
        'Agent 全栈能力：熟悉 ReAct 模式、A2A 协议与 MCP 架构，具备 AI Agent 全栈开发能力',
        'AI 工程化实践：熟练使用 OpenClaw、Claude Code、Cursor 等 AI 工具，可高效完成全流程开发',
        '全栈开发经验：独立完成 Flask + MySQL Web 应用从架构设计到云端部署的完整闭环',
        '快速学习能力：能独立解决开发中的实际问题，善于利用 AI 工具加速学习与开发效率',
    ]
    for s in summaries:
        pdf.bullet(s, indent=4)
    pdf.ln(4)

    # ── 致谢 ──
    pdf.set_font(pdf.cjk_font, '', 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 5, '感谢您花时间阅读我的简历，期待与您进一步交流！', align='C')

    output_path = r'C:\Users\Lenovo\Desktop\张帅谦_简历_优化版.pdf'
    pdf.output(output_path)
    print(f'PDF saved to: {output_path}')

if __name__ == '__main__':
    build()
