# _*_ coding: UTF-8 _*_
import logging
import os
import xml.etree.cElementTree as ET
from wsgiref.simple_server import make_server

import re
import soaplib
from soaplib.core.model.primitive import Integer, String
from soaplib.core.server import wsgi
from soaplib.core.service import DefinitionBase  # 所有服务类必须继承该类
from soaplib.core.service import soap  # 声明注解

from resultCode import Codes
from scripts.db import *
from store.gentask import generateTaskId
from store.writefile import writeXML
from tasks.agent import checkAllLz
from util.fileUtil import calcHash

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S', filename='../logs/server.log', filemode='a')
logger = logging.getLogger('server')


# 验证用户信息
def validateuser(uname, upwd):
    userCheckResult = Users.getOne(Users.userName == uname, Users.userPwd == upwd)
    if userCheckResult is not None:
        return userCheckResult
    return None


#根据所有的任务进行构建结果XML
def buildTaskList(root, tasks):
    tasklist = ET.SubElement(root, 'TaskList')
    for t in tasks:
        task = generateSingleTask(t, tasklist)
        resultList = ET.SubElement(task, 'ResultList')
        results = TaskResult.select().where(TaskResult.taskId==t.taskId)
        for r in results:
            generateSingleTaskResult(r, resultList)

#生成单个任务执行的信息
def generateSingleTask(t, tasklist):
    task = ET.SubElement(tasklist, 'Task')
    ET.SubElement(task, 'TaskId').text = str(t.taskId)
    taskResult = TaskResult.getOne(TaskResult.taskId == t)
    if t.ctime is not None:
        ET.SubElement(task, 'CreateTime').text = t.ctime.strftime('%Y-%m-%d %H:%M:%S')
    else:
        ET.SubElement(task, 'CreateTime').text = ""
    if t.intervalDay is not None:
        ET.SubElement(task, 'IntevalDay').text = str(t.intervalDay)
    else:
        ET.SubElement(task, 'IntevalDay').text = "0"
    listCount = TaskInfo.select().where(TaskInfo.taskResultId == taskResult).count()
    errCount = ErrorWeb.select().where(ErrorWeb.resultId == taskResult).count()
    count = str(listCount + errCount)
    ET.SubElement(task, 'ListCount').text = str(count)
    ET.SubElement(task, 'TaskState').text = str(t.state)
    ET.SubElement(task, 'MissingPackId').text = t.missPackId
    return task

#生成单个任务结果的执行信息
def generateSingleTaskResult(r, resultList):
    result = ET.SubElement(resultList, 'Result')
    ET.SubElement(result, 'ResultId').text = str(r.taskResultId)
    if r.createTime is not None:
        ET.SubElement(result, 'StartTime').text = r.createTime.strftime('%Y-%m-%d %H:%M:%S')
    else:
        ET.SubElement(result, 'StartTime').text = ""
    if r.overTime is not None:
        ET.SubElement(result, 'FinishTime').text = r.overTime.strftime('%Y-%m-%d %H:%M:%S')
    else:
        ET.SubElement(result, 'FinishTime').text = ""
    ET.SubElement(result, 'ResultState').text = str(r.state)
    finishCount = TaskInfo.select().where((TaskInfo.taskResultId == r) &
                                          (TaskInfo.state != '1') & (TaskInfo.state != '6')).count()
    ET.SubElement(result, 'FinishCount').text = str(finishCount)
    waitCount = TaskInfo.select().where((TaskInfo.taskResultId == r) & (TaskInfo.state == '1')).count()
    ET.SubElement(result, 'WaitCount').text = str(waitCount)
    failCount = TaskInfo.select().where((TaskInfo.taskResultId == r) & (TaskInfo.state == '-1')).count()
    ET.SubElement(result, 'FailCount').text = str(failCount)


class FetchService(DefinitionBase):
    """新建任务返回生成的任务编号"""
    @soap(String, String, Integer, Integer, _returns=String)
    def addTask(self, userName, password, taskType, intervalDay):
        # taskType:默认为1
        # intervalDay:不周期检查默认为0
        root = ET.Element("ReturnInfo")
        try:
            user_result = validateuser(userName, password)
            if user_result is not None:
                if taskType >= 0 and intervalDay >= 0:
                    taskId = generateTaskId()
                    t = Task()
                    t.taskId = taskId
                    t.userId = user_result
                    t.taskType = taskType
                    t.intervalDay = intervalDay
                    t.state = 1
                    t.ctime = format(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
                    q = t.save(force_insert=True)
                    if 1 == q:
                        ET.SubElement(root, "State").text = Codes.SUCCESS
                        ET.SubElement(root, "TaskId").text = str(taskId)
                        logger.info("添加任务成功:%s" % taskId)
                    else:
                        ET.SubElement(root, "State").text = Codes.INNERERROR
                        logger.debug("添加任务失败,userName:%s password:%s taskType:%s intervalDay:%s" % (
                            userName, password, taskType, intervalDay))
                else:
                    ET.SubElement(root, "State").text = Codes.PARAMSERROR
                    logger.info("新建任务参数校验失败，taskType:%s,intervalDay:%s:" % (taskType, intervalDay))
            else:
                ET.SubElement(root, "State").text = Codes.USERERROR
                logger.info("用户校验失败，userName:%s,password:%s:" % (userName, password))
        except Exception, e:
            logger.debug(e)
            ET.SubElement(root, "State").text = Codes.INNERERROR

        return ET.tostring(root, encoding="UTF-8")

    # 用于接收用户上传的文件进行等待接收完整后执行亮照检查
    @soap(String, String, String, String, Integer, Integer, Integer, String, _returns=String)
    def sendCheckList(self, userName, password, taskId, checkListData, packId, packCount, listCount, md5Hash):
        # taskId:任务编号
        # userName：用户名
        # password:密码
        # checkListData: 需要抓取的任务--xml格式
        # packId:此xml文件的packageId
        # packCount:需要发送的总包数
        # listCount:本包中包含多少条记录
        # md5Hash:接收成功后XML字符串的md5 hash
        # taskCount：需要发送的任务总数
        root = ET.Element("ReturnInfo")
        try:
            user_result = validateuser(userName, password)
            if user_result is not None:
                taskEnity = Task.getOne(Task.taskId == taskId)
                if taskEnity is not None:
                    if checkListData == "":
                        ET.SubElement(root, "State").text = Codes.PARAMSERROR
                    else:
                        if packId > 0 and packCount > 0 and listCount > 0:
                            # 校验hash
                            strHash = calcHash(checkListData)
                            print 'strHash:',strHash
                            if strHash==md5Hash:
                                ET.SubElement(root, "TaskId").text = taskId
                                dirPath = os.path.abspath(
                                str.format(os.path.join('../temp/{}/'), taskId))
                                if not os.path.exists(dirPath):
                                    os.makedirs(dirPath)
                                filePath = dirPath+"/"+ str(packId) + '.xml'
                                saveResullt = writeXML(filePath, checkListData)
                                if saveResullt is None:
                                    ET.SubElement(root, "State").text = Codes.COMPANYFILEISEXISTS
                                elif saveResullt is True:
                                    # 根据taskId目录下的文件个数判断是否接收完整
                                    fileCount = len(os.listdir('../temp/%s' % taskId))
                                    # 当所有的包完整接收之后进行数据校验再向数据库中添加任务记录
                                    if fileCount == packCount:
                                        # 主任务结果
                                        taskResult = TaskResult()
                                        taskResult.taskId = taskEnity
                                        taskResult.state = '1'
                                        q = taskResult.save(force_insert=True)
                                        if q == 1:
                                            checkAllLz.delay(os.path.abspath(dirPath), taskResult.taskResultId)
                                            ET.SubElement(root, "State").text = Codes.SUCCESS
                                        else:
                                            ET.SubElement(root, "State").text = Codes.INTERIORERROR
                                    else:
                                        ET.SubElement(root, "State").text = Codes.SUCCESS
                            else:
                                # 记录不完整的packid
                                pId = taskEnity.missPackId
                                if pId != "":
                                    packIds = pId + "," + str(packId)
                                else:
                                    packIds = str(packId)
                                q = Task.update(missPackId=packIds).where(Task.taskId == taskId)
                                q.execute()
                                ET.SubElement(root, "State").text = Codes.VALIDERROR
                        else:
                            ET.SubElement(root, "State").text = Codes.PARAMSERROR
                else:
                    ET.SubElement(root, "State").text = Codes.TASKIDERROR
            else:
                ET.SubElement(root, "State").text = Codes.USERERROR
        except Exception, e:
            ET.SubElement(root, "State").text = Codes.INNERERROR
            print e
        return ET.tostring(root, encoding="UTF-8")

    # 获取抓取亮照检查明细结果（返回结果以XML的方式返回）
    @soap(String, String, String, String, Integer, _returns=String)
    def getALResult(self, userName, password, taskId, resultId, packId):
        root = ET.Element("ReturnInfo")
        try:
            user_result = validateuser(userName, password)
            if user_result is not None:
                if taskId != "" and Task.getOne(Task.taskId == taskId) is not None:
                    ET.SubElement(root, "TaskId").text = str(taskId)
                    if resultId!="":
                        taskResultCount  = TaskResult.select().where(TaskResult.taskResultId==resultId).count()
                        if taskResultCount>0:
                            if TaskResult.select().where((TaskResult.taskResultId==resultId) & (TaskResult.taskId==taskId)).count()>0:
                                judgeTaskResult = TaskResult.getOne(TaskResult.taskResultId==resultId)
                                isOver =judgeTaskResult.state
                                if isOver=="1":
                                    ET.SubElement(root, "State").text = Codes.TASKNOCOMPLETE
                                elif isOver=="2":
                                    #根据已经完成的任务生成检查结果明细
                                    self.getCheckTaskList(judgeTaskResult, packId, resultId, root, taskId)
                            else:
                                ET.SubElement(root, "State").text = Codes.PARAMSERROR
                        else:
                            ET.SubElement(root, "State").text = Codes.RESULTIDERROR
                    else:
                        #如果resultId为空，则只取最新的一次已完成的任务结果
                        checkTaskResult = TaskResult.select().order_by(TaskResult.overTime.desc())\
                            .paginate(0, 1).where((TaskResult.state=='2') & (TaskResult.taskId==taskId))
                        if checkTaskResult is not None:
                            for t in checkTaskResult:
                                self.getCheckTaskList(t, packId, resultId, root, taskId)
                        else:
                            checkTaskResult = TaskResult.select().order_by(TaskResult.overTime.desc())\
                            .paginate(0, 1).where((TaskResult.state=='1') & (TaskResult.taskId==taskId))
                            if len(checkTaskResult)>0:
                                ET.SubElement(root, "State").text = Codes.TASKNOCOMPLETE
                else:
                    ET.SubElement(root, "State").text = Codes.TASKIDERROR
            else:
                ET.SubElement(root, "State").text = Codes.USERERROR
        except Exception:
            ET.SubElement(root, "State").text = Codes.INNERERROR
        return ET.tostring(root, encoding="UTF-8")

    def getCheckTaskList(self, judgeTaskResult, packId, resultId, root, taskId):
        if packId > 0:
                packCount = len(os.listdir('../temp/%s' % taskId))
                print "packCount:",packCount
                # 校验packid是否在有效范围内
                if packId > packCount:
                    ET.SubElement(root, "State").text = Codes.PARAMSERROR
                else:
                    self.getCheckListResult(packId, root, taskId,resultId,judgeTaskResult)
        else:
            # PackId为空,默认返回包编号为1的信息
            self.getCheckListResult(1, root, taskId,resultId,judgeTaskResult)


    def getCheckListResult(self, packId, root, taskId,resultId,judgeTaskResult):
        if os.path.exists('../temp/%s/%s.xml' % (taskId, packId)):
            ET.SubElement(root, "ResultId").text = str(resultId)
            listCount = TaskInfo.select().where(TaskInfo.taskResultId == judgeTaskResult).count()
            ET.SubElement(root, "ListCount").text = str(listCount)
            # 获取指定包编号的检查结果信息
            checklistResult = ET.ElementTree(file='../temp/%s/%s.xml' % (taskId, packId))
            checklist = ET.SubElement(root, "CheckList")
            counter = 0
            for elem in checklistResult.iter(tag="CheckItem"):
                checklist.append(elem)
                counter+=1
            fileCheckListString = open('../temp/%s/%s.xml' % (taskId, packId), 'r').read()
            strHash = calcHash(fileCheckListString)
            ET.SubElement(root, "PackCount").text = str(counter)
            ET.SubElement(root, "PackId").text = str(packId)
            ET.SubElement(root, "Md5").text = str(strHash)
            ET.SubElement(root, "State").text = Codes.SUCCESS
        else:
            ET.SubElement(root, "State").text = Codes.INNERERROR

    # 单次巡检的任务结果构建
    def buildSingleTask(self, root, taskId):
        ET.SubElement(root, "State").text = Codes.SUCCESS
        taskinfos = TaskInfo.select(TaskInfo.url, TaskInfo.cname, TaskInfo.state) \
            .where(TaskInfo.taskResultId == (
            TaskResult.select(TaskResult.taskResultId).where(TaskResult.taskId == taskId)))
        listTag = ET.SubElement(root, 'tasks')
        for t in taskinfos:
            dict = ET.SubElement(listTag, "task")
            key = ET.SubElement(dict, "cname")
            key.text = t.cname
            string = ET.SubElement(dict, "url")
            string.text = t.url
            state = ET.SubElement(dict, "state")
            state.text = t.state

    # 添加接收邮件
    @soap(String, String, String, _returns=String)
    def addReceivedMail(self, userName, password, _email):
        root = ET.Element("ReturnInfo")
        if userName == "" or password == "":
            ET.SubElement(root, "State").text = Codes.USERACCOUNTORPASSWORDISEMPTY
        else:
            user_result = validateuser(userName, password)
            if user_result is not None:
                if _email != "" and re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", _email)!=None:
                    q = Users.update(email=_email).where(Users.userId==user_result.userId)
                    count = q.execute()
                    if count >= 1:
                        ET.SubElement(root, "State").text = Codes.SUCCESS
                    else:
                        ET.SubElement(root, "State").text = Codes.INNERERROR
                else:
                    ET.SubElement(root, "State").text = Codes.PARAMSERROR
            else:
                ET.SubElement(root, "State").text = Codes.USERERROR

        return ET.tostring(root, encoding="UTF-8")

    #获取报告
    @soap(String, String, String, String, _returns=String)
    def getALReport(self, userName, password, taskId, resultId):
        pass

    # 获取任务清单
    @soap(String, String, String, String, _returns=String)
    def getTaskList(self, userName, password, taskId, resultId):
        root = ET.Element("ReturnInfo")
        try:
            if userName == "" or password == "" or taskId == "":
                ET.SubElement(root, "State").text = Codes.PARAMSERROR
            else:
                user_result = validateuser(userName, password)
                if user_result is not None:
                    if taskId=="ALL" and resultId=="ALL":
                        #获取所有任务已经完成的任务结果
                        tasks = Task.select().where(Task.userId==user_result)
                        if tasks is not None:
                            buildTaskList(root,tasks)
                    else:
                        task = Task.getOne(Task.taskId==taskId)
                        if task is not None:
                            #任务结果编号为ALL
                            if resultId =="ALL":
                                #获取此任务下的所有任务结果
                                tasklist = ET.SubElement(root, 'TaskList')
                                tempTask = generateSingleTask(task, tasklist)
                                resultList = ET.SubElement(tempTask, 'ResultList')
                                resultsCount = TaskResult.select().where(TaskResult.taskId==task).count()
                                if resultsCount>0:
                                    results = TaskResult.select().where(TaskResult.taskId==task)
                                    for r in results:
                                        generateSingleTaskResult(r, resultList)
                            else:
                                taskResult = TaskResult.getOne(TaskResult.taskResultId == resultId)
                                if taskResult is not None:
                                    tasklist = ET.SubElement(root, 'TaskList')
                                    tempTask = generateSingleTask(task, tasklist)
                                    resultList = ET.SubElement(tempTask, 'ResultList')
                                    generateSingleTaskResult(taskResult, resultList)
                        else:
                            ET.SubElement(root, "State").text = Codes.TASKIDERROR
                else:
                    ET.SubElement(root, "State").text = Codes.USERERROR
        except Exception,e:
            ET.SubElement(root, "State").text = Codes.INNERERROR
            print e
        return ET.tostring(root, encoding="UTF-8")

    # 修改用户密码
    @soap(String, String, String, _returns=String)
    def updatePassword(self, userName, password, newPassword):
        root = ET.Element("ReturnInfo")
        user_result = validateuser(userName, password)
        if user_result is not None:
            try:
                user_result.userPwd = newPassword
                r = user_result.save()
                if r == 1:
                    ET.SubElement(root, "State").text = Codes.SUCCESS
                else:
                    ET.SubElement(root, "State").text = Codes.UPDATEUSERPASSWORDERROR
            except Exception, e:
                ET.SubElement(root, "State").text = Codes.DBERROR
                print e
        else:
            ET.SubElement(root, "State").text = Codes.USERERROR
        return ET.tostring(root, encoding="UTF-8")

    # 取消任务
    @soap(String, String, String, _returns=String)
    def cancelTask(self, userName, password, taskId):
        root = ET.Element("ReturnInfo")
        ET.SubElement(root, "State").text = Codes.SUCCESS
        return ET.tostring(root, encoding="UTF-8")


# 发布webservice服务
def publishservice():
    try:
        soap_application = soaplib.core.Application([FetchService], 'http')
        wsgi_application = wsgi.Application(soap_application)
        server = make_server(config.publishServerIP, config.publishServerPort, wsgi_application)
        server.serve_forever()
        print '发布服务成功'
    except ImportError:
        print 'error'


if __name__ == '__main__':  # 发布服务
    publishservice()
