# _*_coding: UTF-8_*_
from scripts.lzParser import *


# 通过指定的文件路径进行解析html文件中的企业信息为数组类型


def parseHtmlFiles(path):
    results = []
    newResult = []
    tempFile = None
    try:
        files = GetFileFromThisRootDir(path)
        for f in files:
            result = parserFile(f)
            if None is not result and len(result) > 0:
                results.append(result)
        # 使用lambda表达式和reduce结合去除重复文件
        func = lambda x, y: x if y in x else x + [y]
        newResult = reduce(func, [[], ] + results)
        print '文件解析完成,共解析不重复文件:%s个' % len(newResult)
    except Exception, e:
        print '文件解析失败'
        print e
    finally:
        if tempFile is not None:
            tempFile.close()
    return newResult


# 通过指定的文件路径进行解析html文件中的网站信息为数组类型
def parseWebFiles(path):
    results = []
    newResult = []
    tempFile = None
    try:
        files = GetFileFromThisRootDir(path)
        for f in files:
            result = parserWebSite(f)
            if None is not result and len(result) > 0:
                results.append(result)
        # 使用lambda表达式和reduce结合去除重复文件
        func = lambda x, y: x if y in x else x + [y]
        newResult = reduce(func, [[], ] + results)
        print '文件解析完成,共解析不重复文件:%s个' % len(newResult)
    except Exception, e:
        print '文件解析失败'
        print e
    finally:
        if tempFile is not None:
            tempFile.close()
    return newResult




# 根据指定的文件路径进行解析公司信息
def parseHtml(path):
    if path is not None:
        if os.path.exists(path):
            result = parserFile(path)
            return result
        else:
            print '文件不存在'
    else:
        print '文件地址为空'
    return None

# 根据指定的文件路径进行解析公司信息和网站信息
def parseCompanyAndWebsite(path):
    if path is not None:
        if os.path.exists(path):
            result = parserAllFile(path)
            return result
        else:
            print '文件不存在'
    else:
        print '文件地址为空'
    return None
