# _*_coding: UTF-8_*_
# 亮照检查
import csv
import datetime
import os

from scripts.db import Website, Company, impCompanyInfo, \
    impWebsite, \
    TaskInfo


# 网站无法访问
def noAccess(dirPath, filePath, mainTask, shortUrl, subTask):
    dt = format(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
    qw = Website.update(updateDate=dt).where(Website.webId == subTask.webId.webId)
    qw.execute()

    q = TaskInfo.update(state='7').where(TaskInfo.id == subTask.id)
    q.execute()
    # 删除此首页文件
    if os.path.exists(filePath):
        os.remove(filePath)
    # 删除本次任务目录
    if os.path.exists(dirPath):
        os.rmdir(dirPath)


# 没有亮照的处理办法
def judgeNoLz(companyName, shortUrl, subTask):
    dt = format(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
    qw = Website.update(updateDate=dt).where(Website.webId == subTask.webId.webId)
    qw.execute()
    q = TaskInfo.update(state='3').where(TaskInfo.id == subTask.id)
    q.execute()


# 通过公司信息和子任务信息以及公司网址进行检查亮照结果
def judgeLzResult(com, web, shortUrl, subTask):
    # 更新网站信息和公司信息
    impCompanyInfo(com)
    # impWebsite(web)
    # nWeb = Website.getOne(Website.domain == web.domain)

    # judgeWeb = Website.getOne(Website.domain ** str.format("%{}%", shortUrl))

    # 如果查询网址与抓取亮照后的网址不匹配
    if shortUrl != '':
        shortUrl = shortUrl.replace('http://', '').replace(' ', '')
    print  'shortUrl:', shortUrl
    print "web.domain:", web.domain
    com = Company.getOne(Company.coname == com.coname)
    if shortUrl != web.domain:
        # 当已经存在跳转关系记录时,不再操作
        existsJumpWeb = Website.getOne((Website.domain == web.domain))
        if existsJumpWeb is None:
            dt = format(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
            web.updateDate = dt
            web.regID = com
            web.save(force_insert=True)
            # 更新网站跳转地址
            q = Website.update(jump=web).where(Website.webId == subTask.webId.webId)
            q.execute()
        else:
            impWebsite(web)
            # 更新网站跳转地址
            q = Website.update(jump=existsJumpWeb).where(Website.webId == subTask.webId.webId)
            q.execute()
    else:
        #更新网站信息
        impWebsite(web)

    count = Website.select().where(
            (Website.licID != '') & (Website.regID == com) & (Website.domain == shortUrl)
    ).count()
    if count == 0:
        onlyCname = Website.select().where(
                (Website.licID != '') & (Website.regID == com)).count()
        onlyDomain = Website.select().where(
                (Website.licID != '') & (Website.domain == shortUrl)).count()
        if onlyCname > 0:
            q = TaskInfo.update(state='9').where(TaskInfo.id == subTask.id)
            q.execute()
        elif onlyDomain > 0:
            q = TaskInfo.update(state='8').where(TaskInfo.id == subTask.id)
            q.execute()
        else:
            q = TaskInfo.update(state='4').where(TaskInfo.id == subTask.id)
            q.execute()
    else:
        q = TaskInfo.update(state='2').where(TaskInfo.id == subTask.id)
        q.execute()


# 解析csv文件为list类型
def parseFileByCSV(filePath):
    datas = csv.reader(open(filePath, 'rb'))
    dataList = []
    i = 0
    for line in datas:
        if i != 0:
            if line != []:
                dataList.append(line)
        i += 1
    return dataList


# 解析文件类型为XML格式的数据
def parseFileByXML(filePath):
    pass
