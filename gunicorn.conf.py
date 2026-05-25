bind = "0.0.0.0:8000"
workers = 3
worker_class = "sync"
timeout = 120
accesslog = "-"
errorlog = "-"
loglevel = "info"

# 生产环境建议通过反向代理运行，去掉下面注释：
# bind = "unix:/tmp/taskhub.sock"
# workers = 4
