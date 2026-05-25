# PythonAnywhere WSGI 配置
# 在 PythonAnywhere Web 配置页面中：
#   Source code: /home/你的用户名/taskhub
#   Working directory: /home/你的用户名/taskhub
#   WSGI configuration file: /var/www/你的用户名_pythonanywhere_com_wsgi.py
#
# 将下面内容粘贴到 WSGI configuration file 中：

import sys
import os

# 项目路径
project_home = '/home/你的用户名/taskhub'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# 环境变量（在这里设置，不需要 .env 文件）
os.environ['DB_HOST'] = '你的用户名.mysql.pythonanywhere-services.com'
os.environ['DB_USER'] = '你的用户名'
os.environ['DB_PASSWORD'] = '你设置的数据库密码'
os.environ['DB_NAME'] = '你的用户名$taskhub'
os.environ['SECRET_KEY'] = '随机字符串用 openssl rand -hex 32 生成'
os.environ['FLASK_DEBUG'] = '0'

from app import create_app
application = create_app()
