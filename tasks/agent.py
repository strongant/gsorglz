# _*_coding: UTF-8_*_
from __future__ import absolute_import

import datetime
import gc
import json
import logging
import math
import os
import re
import smtplib
import subprocess
from email.header import Header
from email.mime.text import MIMEText
from email.utils import formataddr
from email.utils import parseaddr

from apscheduler.schedulers.background import BackgroundScheduler
from celery.utils.log import get_task_logger
from errand_boy.transports.unixsocket import UNIXSocketTransport

import config
from app import celery
from dao.EsDao import send2esBulk, sendSingleObjToEs
from scripts.lzParser import parserCompanyAndWeb
from service.WebUtil import getGsLzUrl, getGsLzId
from util.fileUtil import parseXMLFile

errand_boy_transport = UNIXSocketTransport()

# 获取日志对象
from scripts.db import Website, TaskInfo, buildCompany, buildWebsite, Configs, Task, TaskResult, Company, psql_db
from service.MakeLz import noAccess, judgeLzResult, judgeNoLz
from util.urlUtil import validateUrl
import xml.etree.cElementTree as ET

#logging.basicConfig(filename=config.LOGGER_PATH,level=logging.DEBUG)
# logger = logging.getLogger('agent')
# logger.setLevel(logging.DEBUG)
#
# fh = logging.FileHandler('../logs/agent.log')
# fh.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# fh.setFormatter(formatter)
#
#
# logger.addHandler(fh)





#mongoengine.connect(host=config.MONGODB_URL)

# 任务调度apscheduler
# scheduler = BackgroundScheduler(jobstores=config.jobstores, executors=config.executors,
#                                     job_defaults=config.job_defaults,
#                                     timezone=config.timezone)
scheduler = BackgroundScheduler(jobstores=config.jobstores, executors=config.executors,
                                     job_defaults=config.job_defaults,
                                     timezone=config.timezone)

# def makeScheduler():
#
#     if not scheduler.running:
#         try:
#             scheduler.start()
#         except Exception, e:
#             print e
#     return scheduler
#
#
# scheduler = makeScheduler()


# 向es存储解析的网址信息
@celery.task
def sendPageDataToEs(index, type, builkUrlList):
    try:
        result = None
        # 批量插入时，当插入的文档超过10000条时应该进行一次bulk，不能执行超过10000个文档的插入
        if len(builkUrlList) >= 10000:
            tempCount = 0
            tempArr = []
            for url in range(builkUrlList):
                tempCount += 1
                if tempCount >= 9000:
                    bulkjsonStr = "".join(builkUrlList)
                    send2esBulk(index, type, bulkjsonStr)
                    tempCount = 0
                else:
                    tempArr.append(url)
            bulkjsonStr = "".join(tempArr)
            send2esBulk(index, type, bulkjsonStr)
        else:
            bulkjsonStr = "".join(builkUrlList)
            print 'bulkjsonStr', bulkjsonStr
            result = send2esBulk(index, type, bulkjsonStr)
        print 'es,result:', result
        return result
    except Exception, e:
        print e
        return e


# 根据url地址进行下载相应的首页html
# @celery.task
# def fetch_page(url, file_path):
#     return download(url, file_path)


# 通过正则表达式提取网页中有用的内容
@celery.task
def pass_page(file_path):
    '''
    调用linux的shell进行格式化需要的数据
    '''
    handle = subprocess.Popen("grep -Po '(?<=\>)[^\<|\>|^\<script|\>]*(?=\<)' %s" % file_path, shell=True,
                              stdout=subprocess.PIPE)
    # 将文本内容去空格和换行
    content = ''.join(handle.communicate()[0].split())
    return content


# 将网页中的文本信息存储到es
@celery.task(ignore_result=True)
def store_page_info(index, type, url, taskid, content):
    data = {
        "url": url,
        "taskid": taskid,
        "content": content
    }
    pageData = json.dumps(data)
    sendSingleObjToEs(index, type, pageData)


# 通过celery的chain方式进行调度任务
# def create_page_info(url, urlFilePath, taskid, index, type):
#     # 通过Url地址进行抓取网站首页内容，将原始内容存储到../data目录下，然后解析原始内容保存到es下
#     filePath = fetch_page.delay(url, urlFilePath)
#     contentResult = pass_page.delay(filePath.get())
#     pageContent = contentResult.get()
#     print 'content.get():', pageContent
#     store_page_info.delay(index, type, url, taskid, pageContent)


def downloadByPhantom(phantomjs_path, scarping_js_path,
                      url, save_path, charset,
                      request_timeout, timeout,
                      cookies, headers):
    args = [phantomjs_path,
            '--ssl-protocol=any', scarping_js_path,
            url, save_path, charset, request_timeout,
            timeout, json.dumps(cookies),
            json.dumps(headers)]
    env = getattr(os, 'environb', os.environ)
    formated_env = {}
    for key, value in env.iteritems():
        if isinstance(key, unicode):
            try:
                key = key.encode(charset)
            except Exception:
                key = key.encode('utf-8', errors='ignore')
        if isinstance(value, unicode):
            try:
                value = value.encode(charset)
            except Exception:
                value = value.encode('utf-8', errors='ignore')
        formated_env[key] = value
    gc.collect()
    with errand_boy_transport.get_session() as session:
        subprocess = session.subprocess
        process = subprocess.Popen(args, close_fds=True, env=formated_env)
        status = process.wait()
    return status


# 抓取亮照页面
def fetchLzPage(isLzUrl, lzPath, shortUrl, subTask):
    # 根据亮照的完整url进行抓取
    status = downloadByPath(isLzUrl, lzPath)
    if not os.path.exists(lzPath):
        print "lzpath:",lzPath
        #logger.debug('亮照页面无法访问:', isLzUrl)
        #dt = format(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
        # qw = Website.update(updateDate=dt).where(Website.webId == subTask.webId.webId)
        # qw.execute()
        q = TaskInfo.update(state='5', remark=isLzUrl).where(TaskInfo.id == subTask.id)
        q.execute()
    else:
        try:
            f = open(lzPath, 'r')
            parseData = parserCompanyAndWeb(f.read())
            com = buildCompany(parseData['company'])
            tempBuildWeb = buildWebsite(parseData['web'])
            judgeLzResult(com, tempBuildWeb, shortUrl, subTask)
        except Exception, e:
            print e
            #logger.debug('亮照页面无法访问:', isLzUrl)
            # q = TaskInfo.update(state='5', remark=isLzUrl).where(TaskInfo.id == subTask.id)
            # q.execute()


def downloadByPath(url, filePath):
    return downloadByPhantom(config.PHANTOMJS_PATH, config.SCARPING_JS_PATH,
                             url, filePath, 'utf-8', str(config.request_timeout), str(config.timeout), '', '')


# 进行解析亮照信息
def makeWeb(companyName, filePath, mainTask, shortUrl, subTask):
    # 检查网站首页是否包含工商亮照标识
    isLzUrl = getGsLzUrl(filePath)
    if isLzUrl == '':
        # 没有亮照标识的处理方法
        judgeNoLz(companyName, shortUrl, subTask)
    else:
        lzId = getGsLzId(isLzUrl)
        lzPathName = '%s.html' % lzId
        lzPath = os.path.abspath(os.path.dirname('./lz/')) + '/%s' % lzPathName
        fetchLzPage(isLzUrl, lzPath, shortUrl, subTask)


# 通过指定的url进行抓取网站信息
def fetchWebsite(companyName, bigTaskId, subTaskId, url):
    mainTask = Task.getOne(Task.taskId == bigTaskId)
    subTask = TaskInfo.getOne(TaskInfo.id == subTaskId)
    # 每一个新的任务存放首页的目录格式为:网站域名+任务编号+任务结果编号+企业首页信息------------->如:www.yummy77.com/123456789/1/www.yummy77.com.html
    dirPath = os.path.abspath(
            str.format(os.path.join('./data/{}/{}/{}/'), url, bigTaskId, subTask.taskResultId.taskResultId))
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)

    filePath = dirPath + '/' + url + '.html'
    # 如果url中没有http://，则对其进行添加
    if url.find('http://') == -1:
        url = "http://%s" % url
    # 进行抓取操作,然后对其进行亮照结果筛选
    status = downloadByPhantom('/usr/bin/phantomjs', os.path.abspath('./phantomjs/fetch.js'),
                               url, filePath, 'utf-8', str(config.request_timeout), str(config.timeout), '', '')
    if not os.path.exists(filePath):
        #logger.debug('主页无法访问:', url)
        # 无法访问
        noAccess(dirPath, filePath, mainTask, url, subTask)
    else:
        # 检查网站首页是否包含工商亮照标识
        webContent = open(filePath, 'r').read()
        # 返回的结果类似于<html><head></head><body></body></html>
        noContent = re.match('.*<body></body>', webContent)
        # 返回空白结果
        blankContent = len(webContent)
        # 返回纠错网址结果
        errorSite = webContent.find('网址纠错')
        # 网站主页无法访问
        if noContent is not None or blankContent == 0 or errorSite != -1:
            # 按照无法访问处理
            noAccess(dirPath, filePath, mainTask, url, subTask)
        else:
            # 对网站首页进行解析并检查
            makeWeb(companyName, filePath, mainTask, url, subTask)


# 已经存在并且没有过期的网站信息处理
def isAlreadyExistsWeb(companyName, currentTime, expired, shortUrl, subTaskId, url, isExistsWebId):
    subTask = TaskInfo.getOne(TaskInfo.id == subTaskId)
    taskResult = subTask.taskResultId
    bigTask = taskResult.taskId
    bigTaskId = bigTask.taskId
    # 获取当前网站上一次的更新时间
    websiteResult = Website.getOne(Website.webId == isExistsWebId)
    webUpdateTime = websiteResult.updateDate
    if webUpdateTime is None:
        diffDay = expired + 1
    else:
        diffDay = (currentTime - webUpdateTime).days
    if diffDay > expired:
        print '时间已经过期'
        # 网站信息过期,需要重新抓取并检测
        fetchWebsite(companyName, bigTaskId, subTaskId, url)
    else:
        # 判断是否有当前网站信息是否存在亮照编号
        if websiteResult.licID != '':
            #logger.debug('已经亮照:', shortUrl)
            q = TaskInfo.update(state='2').where(TaskInfo.id == subTaskId)
            q.execute()
        else:
            #logger.debug('未亮照:', shortUrl)
            q = TaskInfo.update(state='3').where(TaskInfo.id == subTaskId)
            q.execute()


@celery.task
def fetchCycle(subtaskId, taskResultId, delayTag):
    if delayTag:
        checkTaskResult = TaskResult.getOne(TaskResult.taskResultId == taskResultId)
        bigTaskId = checkTaskResult.taskId.taskId
        # 根据任务结果编号获取本次需要检查的任务记录
        subTask = TaskInfo.getOne(TaskInfo.id == subtaskId)
        if subTask is not None:
            companyName = subTask.cname
            url = subTask.url
            # 抓取检测
            fetchWebsite(companyName, bigTaskId, subTask.id, url)
        else:
            print 'taskinfo记录为空:', subTask
            #logger.debug('taskinfo记录为空:', subTask)


@celery.task
def checkLz(subtaskId):
    try:
        # 根据任务结果编号获取本次需要检查的任务记录
        subTask = TaskInfo.getOne(TaskInfo.id == subtaskId)
        checkTaskResult = subTask.taskResultId
        bigTaskId = checkTaskResult.taskId.taskId
        if subTask is not None:
            companyName = subTask.webId.regID.coname
            url = subTask.webId.domain
            if (validateUrl(url)):
                # 从任务表中获取是否已经进行检查过了(根据网站有没有更新时间进行判断)
                isExistsTask = TaskInfo.getOne(
                        TaskInfo.webId == Website.getOne((Website.domain == url) & (Website.updateDate.is_null(False))))
                subId = subTask.id
                # 数据库中无此task对应的网站记录
                if isExistsTask is None:
                    # 抓取检测
                    fetchWebsite(companyName, bigTaskId,subId, url)
                else:
                    isExistsWebId = isExistsTask.webId.webId
                    # 如果当前网站更新时间小于过期时间,说明不用重新进行抓取并检查
                    expired = Configs.getOne(Configs.type == 'update').expired
                    # 获取当前时间
                    currentTime = datetime.datetime.now()
                    isAlreadyExistsWeb(companyName, currentTime, expired, url, subId,
                                       url,
                                       isExistsWebId)
    except Exception:
        q = TaskInfo.update(state='-1')
        q.execute()


# 单次任务处理
def executeOnceTaskInfo(taskResultId):
    # 获取celery中当前已经正在进行的任务数
    nowCount = TaskInfo.select().where((TaskInfo.state == '6')).count()
    # 当celery中正在做的任务数量少于指定的数量时，向celery添加需要执行的任务
    if nowCount <= config.celeryMaxCount:
        taskCount = TaskInfo.select().where(
                (TaskInfo.state == '1') & (TaskInfo.taskResultId == taskResultId)).count()
        print 'taskCount:', taskCount
        if taskCount == 0:
            singalCheck(taskResultId)
        else:
            tasks = TaskInfo.select().order_by(TaskInfo.id).paginate(0, config.sendCeleryCount).where(
                    (TaskInfo.taskResultId == taskResultId) & (TaskInfo.state == '1'))
            for subTask in tasks:
                subtaskId = subTask.id
                checkLz.apply_async((subtaskId,), queue="celery")
                # 更新taskinfo状态为已发送
                q = TaskInfo.update(state='6').where(TaskInfo.id == subtaskId)
                q.execute()


# 用于处理任务完成之后发邮件和更新任务结果记录
def singalCheck(taskResultId):
    # 根据任务编号查询所有任务是否已经完成
    executeCount = TaskInfo.select().where(
            (TaskInfo.taskResultId == taskResultId) & (TaskInfo.state != 1) & (TaskInfo.state != 6)).count()
    subTaskResult = TaskInfo.select().where(TaskInfo.taskResultId == taskResultId).count()
    print 'subTaskResult', subTaskResult
    print 'executeCount', executeCount
    if executeCount == subTaskResult and executeCount != 0:
        #将本次任务检查结果明细生成到result目录
        checkTaskResult = TaskResult.getOne(TaskResult.taskResultId == taskResultId)
        taskId = checkTaskResult.taskId.taskId
        result_taskresultid = checkTaskResult.taskResultId
        taskCount = TaskInfo.select().where(
                (TaskInfo.taskResultId == taskResultId)).count()
        onceCount = config.getTaskResultCount
        packCount = int(math.ceil(float(taskCount)/float(onceCount)))
        #生成检查结果明细文件
        print '开始生成检查结果明细文件'
        print 'packCount:',packCount
        genTaskResultFile(taskId,result_taskresultid,packCount)


        print '单次任务检查完毕结束当前任务,开始发送邮件通知'
        # 说明该任务结果已经发送完毕，从apscheduler任务调度中删除该任务
        scheduler.remove_job(str(taskResultId))

        bigTaskId = checkTaskResult.taskId.taskId
        taskResultId = checkTaskResult.taskResultId
        # 更新上一次子任务的状态
        oTime = format(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
        q = TaskResult.update(state="2", overTime=oTime).where(
                TaskResult.taskResultId == taskResultId)
        q.execute()
        #修改任务结果对应的大任务状态为已完成
        q = Task.update(state="2").where(Task.taskId==taskId)
        q.execute()
        # 任务执行完毕后发送邮件通知
        mutil = MailUtil()
        # 获取当前任务绑定的邮箱账号
        toEmail = TaskResult.getOne(TaskResult.taskResultId == taskResultId).taskId.userId.email
        if toEmail is not None:
            from_addr = config.SEND_EMAIL
            password = config.SEND_EMAIL_PASSWORD
            to_addr = toEmail
            smtp_server = config.SMTP_SERVER
            msg = str.format(config.MAIL_NOTICE, bigTaskId, bigTaskId, str(taskResultId))
            subject = config.MAIL_SUBJECT
            mutil.sendMail.delay(from_addr, password, to_addr, smtp_server, msg, subject)
        else:
            print "该任务未绑定接收邮箱,任务结果编号:",taskResultId


# 轮巡任务中的间隔任务
def intervalDelayTask(taskResultId):
    # 获取celery中当前已经正在进行的任务数
    nowCount = TaskInfo.select().order_by(TaskInfo.id).where((TaskInfo.state == '6'))
    if nowCount >= 0:
        # 当celery中正在做的任务数量少于指定的数量时，向celery添加需要执行的任务
        if nowCount <= config.celeryMaxCount:
            taskCount = TaskInfo.select().where(
                    (TaskInfo.state == '1') & (TaskInfo.taskResultId == taskResultId)).count()
            print 'taskCount:', taskCount
            if taskCount == 0:
                singalCheck(taskResultId)
                # 查询该任务设置的延迟时间开启下一次需要检查的任务
                interval = Task.getOne(Task.taskId == (
                    TaskResult.select(TaskResult.taskId).where(TaskResult.taskResultId == taskResultId))).intervalDay
                print 'interval:', interval
                if interval != "":
                    # 生成需要轮巡的新主任务结果记录
                    taskResult = TaskResult()
                    lastTaskResult = TaskResult.getOne(TaskResult.taskResultId == taskResultId)
                    taskResult.taskId = lastTaskResult.taskId
                    taskResult.state = '1'
                    taskResult.save()

                    #将上一次的任务结果编号所对应的webId指定给新的任务结果
                    psql_db.transaction()
                    try:
                        query = (TaskInfo
                            .insert_from(
                                fields=[TaskInfo.webId],
                                query=TaskInfo.select(TaskInfo.webId).where(TaskInfo.taskResultId == lastTaskResult)))
                        query.execute()
                        q = TaskInfo.update(taskResultId=taskResult).where(TaskInfo.taskResultId.is_null())
                        q.execute()
                    except Exception, e:
                        print e
                        psql_db.rollback()
                    # 获取当前时间
                    ctime = datetime.datetime.now()
                    delay_time = int(interval)
                    stime = ctime + datetime.timedelta(seconds=delay_time)
                    scheduler.add_job(intervalDelayTask, "date", next_run_time=stime, args=[taskResult.taskResultId],
                                      jobstore="default", id=taskResult.taskResultId)
            else:
                tasks = TaskInfo.select().order_by(TaskInfo.id).paginate(0, config.sendCeleryCount).where(
                        (TaskInfo.taskResultId == taskResultId) & (TaskInfo.state == '1'))
                for subTask in tasks:
                    subtaskId = subTask.id
                    fetchCycle.apply_async((subtaskId,), queue="celery")
                    # 更新taskinfo状态为已发送
                    q = TaskInfo.update(state='6').where(TaskInfo.id == subtaskId)
                    q.execute()


# 单个任务处理
def executeSingleTaskInfo(taskResultId):
    scheduler.add_job(executeOnceTaskInfo, "interval", seconds=10, args=[taskResultId], jobstore="default",
                      id=str(taskResultId))
    if not scheduler.running:
        scheduler.start()


# 轮循任务处理
def executeMultiTaskInfo(taskResultId):
    # 设置interval
    scheduler.add_job(intervalDelayTask, "interval", seconds=20, args=[taskResultId], jobstore="default", id=taskResultId)


@celery.task()
def checkAllLz(filePath, taskResultId):

    taskResult = TaskResult.getOne(TaskResult.taskResultId == taskResultId)
    delayDay = taskResult.taskId.intervalDay
    #根据当前任务编号目录获取该目录下的所有xml文件
    print '目录路径:',filePath
    fnames=os.listdir(filePath)
    for name in fnames:
        xmlName = filePath+'/'+name
        print 'xmlName:',xmlName
        data = parseXMLFile(xmlName, 'CheckItem')
        print 'data:',data
        # 将需要检查的信息入库
        for d in data:
            cname = d.get('cname')
            url = d.get('url')
            if url != '':
                if url[-1] == '/':
                    url = url.replace('http://', '')[0:-1].replace(' ','')
            if cname!='':
                cname = cname.replace(' ','')
            webArea = d.get('area')
            webtype = d.get('WebType')
            # 检查更新company
            if Company.getOne(Company.coname == cname) is None:
                c = Company()
                c.coname = cname
                c.save(force_insert=True)
            # 检查更新website
            if Website.getOne(Website.domain == url) is not None:
                q = Website.update(domain=url, type=webtype, area=webArea).where(Website.domain == url)
                q.execute()
            else:
                com = Company.getOne(Company.coname == cname)
                w = Website()
                w.regID = com
                w.domain = url
                w.area = webArea
                w.type = webtype
                w.save(force_insert=True)
            updateWeb = Website.getOne(Website.domain == url)
            subTask = TaskInfo()
            subTask.taskResultId = taskResult
            subTask.webId = updateWeb
            subTask.state = '1'
            subTask.save(force_insert=True)

    taskResultId = str(taskResultId)
    if delayDay > 0:
        # 需要周期执行的任务
        executeMultiTaskInfo(taskResultId)
    else:
        #logger.debug("开始调用单次任务")
        # 单次执行的任务
        executeSingleTaskInfo(taskResultId)


# 轮循巡查的任务,重新抓取存在相关记录则修改
def intervalFetch(taskResultId, lastTaskResultId, delayTag):
    # 获取上次任务taskResultId
    taskInfos = TaskInfo.select().where(TaskInfo.taskResultId == lastTaskResultId)
    for task in taskInfos:
        subTask = TaskInfo()
        subTask.taskResultId = taskResultId
        subTask.state = ''
        subTask.cname = task.cname
        subTask.url = task.url
        subTask.save(force_insert=True)
        fetchCycle.apply_async((subTask.id, taskResultId, delayTag), queue="celery")


def generateXMLString(taskinfos, rootXML, listTag):
    root = ET.fromstring(rootXML)
    listTag = ET.SubElement(root, listTag)
    for t in taskinfos:
        dict = ET.SubElement(listTag, "task")
        key = ET.SubElement(dict, "cname")
        key.text = t.cname
        string = ET.SubElement(dict, "url")
        string.text = t.url
        state = ET.SubElement(dict, "state")
        state.text = t.state
    return ET.tostring(root)


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((
        Header(name, 'utf-8').encode(),
        addr.encode('utf-8') if isinstance(addr, unicode) else addr))


# 发送邮件
class MailUtil:
    @celery.task(bind=True, max_retries=3)
    def sendMail(self, from_addr, password, to_addr, smtp_server, msg, subject):
        try:
            msg = MIMEText(msg, 'plain', 'utf-8')
            msg['From'] = _format_addr(u'巡检中心 <%s>' % from_addr)
            msg['To'] = _format_addr(u'管理员 <%s>' % to_addr)
            msg['Subject'] = Header(subject, 'utf-8').encode()
            server = smtplib.SMTP(smtp_server, 25)
            server.set_debuglevel(1)
            server.login(from_addr, password)
            server.sendmail(from_addr, [to_addr], msg.as_string())
            server.quit()
        except Exception, e:
            # 发送失败后1分钟后重试
            self.retry(countdown=60 * 1, exc=e)
            print e


#根据任务编号,任务结果编号生成检查结果明细文件
def genTaskResultFile(taskId,taskResultId,packCount):
    onceCount = config.getTaskResultCount
    for i in range(packCount):
        taskinfos = TaskInfo.select().order_by(TaskInfo.id).paginate(i+1, onceCount).where(
                        (TaskInfo.taskResultId == taskResultId))
        listTag = ET.Element('CheckList')
        #1 – 正常亮照
        # -1 – 未亮照
        # -2 – 无法访问
        # -3 – 亮照信息错误
        # -4:公司名称不一致
        # -5:网址不一致
        # -6:抓取异常失败
        for t in taskinfos:
            checkItem = ET.SubElement(listTag, 'CheckItem')
            ET.SubElement(checkItem, 'Coname').text = t.webId.regID.coname
            ET.SubElement(checkItem, 'url').text = t.webId.domain
            ET.SubElement(checkItem, 'area').text = t.webId.area
            ET.SubElement(checkItem, 'WebType').text = t.webId.type
            checkResult = ""
            if t.state=="2":
                checkResult+="1"
            elif t.state=="3":
                checkResult+="-1"
            elif t.state=="4":
                checkResult+="-3"
            elif t.state=="5" or t.state=="7":
                checkResult+="-2"
            elif t.state=="8":
                checkResult+="-4"
            elif t.state=="9":
                checkResult+="-5"
            elif t.state=="-1":
                checkResult+="-6"
            ET.SubElement(checkItem, 'ALResult').text = t.state
        listTagString =ET.tostring(listTag,encoding="UTF-8").replace("<?xml version='1.0' encoding='UTF-8'?>","")
        dirPath = os.path.abspath(
            str.format(os.path.join('./result/{}/{}/'),  taskId, taskResultId))
        if not os.path.exists(dirPath):
            os.makedirs(dirPath)
        fname = '%s/%s.xml'%(dirPath,str(i+1))
        print 'fname:',fname
        f = open(fname,'a')
        f.write(listTagString)
        f.flush()
        f.close()

