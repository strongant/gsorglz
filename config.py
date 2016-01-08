# _*_ coding: UTF-8 _*_
from __future__ import absolute_import

import os

from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

# celery config
BROKER_URL = 'redis://guest@localhost//0'
CELERY_RESULT_BACKEND = 'redis://guest@localhost//1'

CELERY_TASK_RESULT_EXPIRES = 3600
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_RESULT_SERIALIZER = 'json'

CELERY_DEFAULT_EXCHANGE = 'celery'
# CELERY_DEFAULT_EXCHANGE_TYPE = 'direct'
CELERY_DEFAULT_QUEUE = 'celery'
CELERY_DEFAULT_ROUTING_KEY = 'celery'

CELERY_TIMEZONE = 'Asia/Shanghai'
CELERY_ENABLE_UTC = True
CELERY_DISABLE_RATE_LIMITS = True
CELERY_ACKS_LATE = True
CELERY_IGNORE_RESULT = True
CELERYD_CONCURRENCY = 1

# Enables error emails.
CELERY_SEND_TASK_ERROR_EMAILS = True
# ADMINS = (
#     ("{ADMINSUSER}", "{ADMINSEMAIL}"),
# )
#mail setting
SEND_EMAIL = "18215361994@163.com"
EMAIL_PORT = 25
SEND_EMAIL_PASSWORD = "baiwenhui1994"
SMTP_SERVER = "smtp.163.com"

#mail info setting
MAIL_NOTICE = "您好，您提交的{}任务已经检查完毕，请注意查收检查结果.本次任务编号为:{},任务结果编号为:{}."
MAIL_SUBJECT = "来自上海浦东软件园信息技术工商巡检平台"

#mongodb setting
MONGODB_URL = "mongodb://127.0.0.1/apscheduler"

# CELERT_QUEUES = (
#     Queue('default', exchange='default', routing_key='default'),
#     Queue('machine1', exchange='tasks.agent', routing_key='machine1'),
#     Queue('machine2', exchange='tasks.agent', routing_key='machine2')
# )

# CELERY_ROUTES = {
#     'tasks.agent.sendPageDataToEs': {'queue': 'machine1', 'routing_key': 'machine1'},
#     'tasks.agent.intervalFetch': {'queue': 'machine1', 'routing_key': 'machine1'},
#     'tasks.agent.fetch_page': {'queue': 'machine1', 'routing_key': 'machine1'},
#     'tasks.agent.store_page_info': {'queue': 'machine1', 'routing_key': 'machine1'},
#     # 'tasks.agent.checkAllLz': {'queue': 'machine1', 'routing_key': 'machine1'},
#     'tasks.agent.checkLz': {'queue': 'machine1', 'routing_key': 'machine1'},
#     'tasks.agent.fetchCycle': {'queue': 'machine1', 'routing_key': 'machine1'},
#     # 'tasks.agent.checkAllLzByInterval': {'queue': 'machine1', 'routing_key': 'machine1'},
#     # 'tasks.agent.fetchWebsite': {'queue': 'machine1', 'routing_key': 'machine1'},
# }

# logs config
LOGGER_PATH = '/home/devbwh/PycharmProjects/gslz/logs/agent.log'

# db  config
dbIP = '127.0.0.1'
dbPort = 5432
dbUser = 'postgres'
dbPWD = '123456'
dbName = 'lzjc'


#需要解析的数据库连接地址
impDbIP = '10.0.5.30'
impDbPort = 5432
impDbUser = 'postgres'
ImpDbPWD = '123456'
impDbName = 'gs'

#ES配置连接地址
ES_HOST = '127.0.0.1'
ES_PORT = '9200'


# phantomjs params config
# request 超时 60毫秒
request_timeout = 60000
# 打开网站等待30毫秒
timeout = 30000
SCARPING_JS_DIR_PATH =\
os.path.realpath(os.path.join(os.path.dirname(__file__), 'phantomjs'))
SCARPING_JS_PATH =\
os.path.realpath(os.path.join(SCARPING_JS_DIR_PATH,'fetch.js'))
#phantomjs execute path
PHANTOMJS_PATH = "/usr/bin/phantomjs"


# Apscheduler  config start
jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
#'mongo': MongoDBJobStore()
}
executors = {
    'default': ThreadPoolExecutor(20),
    'processpool': ProcessPoolExecutor(5)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 3
}
timezone = "Asia/Shanghai"
# Apscheduler  config  end


# celery 设定任务配置开始
# 规定celery中最大执行任务的数量
celeryMaxCount = 1000
# 规定每次向celery发送的任务数量
sendCeleryCount = 500
#设定任务全部接收完整之后间隔多长时间向celery进行发送任务

# celery 设定任务配置结束

#设置每次获取检查结果的数量
getTaskResultCount = 10000

#设置webservice发布的IP地址
publishServerIP = "10.10.185.234"
#设置webservice发布的端口
publishServerPort = 7790
