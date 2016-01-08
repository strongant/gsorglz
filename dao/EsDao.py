# _*_ coding: UTF-8 _*_
import config
from util.httpUtil import httpPOST


# 用于操作ES的数据访问对象
def sendSingleObjToEs(index, type, data):
    '''
        index:索引名称
        type:表名称
        data:需要插入的数据
    '''
    execute = str.format('/{}/{}/', index, type)
    result = httpPOST(config.ES_HOST, config.ES_PORT, execute, data)
    return result


# 向ES中批量插入数据
def send2esBulk(index, type, data):
    '''
    向ES中的某个type下新增批量数据
    '''
    execute = str.format('/{}/{}/_bulk', index, type)
    print execute
    result = httpPOST(config.ES_HOST, config.ES_PORT, execute, data)
    return result
