# _*_coding: UTF-8_*_
# coding: utf-8

from celery import Celery
from celery.utils.log import get_task_logger
from flask import Flask

# 获取日志对象


logger = get_task_logger(__name__)



flask = Flask(__name__)

# 创建celery对象
def make_celery(app):
    logger.debug('开始初始化celery对象')
    celery = Celery(app.name, include='tasks.agent')
    celery.config_from_object('config')
    celery.conf.update(app.config)
    return celery


celery = make_celery(flask)


@flask.route('/')
def index():
    try:
        pass
        # 将url中的地址进行下载到相应的目录
        # downloadbyurl.apply_async(args=['www.taobao.com','data'],queue='machine1',routing_key='machine1')
    except Exception as e:
        logger.debug(e)
    return 'ok'
    # result = add_together.apply_async(args=[122,34],queue='machine1',routing_key='machine1')
    # return str(result.get())


if __name__ == '__main__':
    # 开启webservice服务
    # publishservice()
    flask.run(debug=True)
