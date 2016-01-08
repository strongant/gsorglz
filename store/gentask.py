# _*_ coding: UTF-8 _*_

# 生成本次任务的taskid
import uuid


def generateTaskId():
    return uuid.uuid1()
