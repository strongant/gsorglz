# _*_coding: UTF-8_*_

import datetime
import sys

from peewee import *

import config

reload(sys)
sys.setdefaultencoding("utf-8")

dbIP = config.dbIP
dbPort = config.dbPort
dbUser = config.dbUser
dbPWD = config.dbPWD
dbName = config.dbName

# init db
psql_db = PostgresqlDatabase(dbName, user=dbUser, password=dbPWD, host=dbIP)


# base
class BaseModel(Model):
    class Meta:
        database = psql_db

    @classmethod
    def getOne(cls, *query, **kwargs):
        try:
            return cls.get(*query, **kwargs)
        except DoesNotExist:
            return None


# Users
class Users(BaseModel):
    userId = PrimaryKeyField(unique=True)
    userName = CharField(max_length=50, unique=True)
    userPwd = CharField(max_length=50)
    userRole = CharField(default='Normal', max_length=50)
    createDate = DateTimeField(default=datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S'))
    email = CharField(max_length=50)


# 工商信息
class GsOrg(BaseModel):  # 工商
    orgID = CharField(default='')  # 原始机关编号
    name = CharField(default='')  # 机关名称
    upOrg = CharField(default='000000')  # 上级机关
    address = CharField(default='')  # 机关地址
    tel = CharField(default='')  # 机关电话


# 企业基本信息
class Company(BaseModel):
    coname = CharField(default='')  # 企业名称
    regID = CharField(unique=True)  # 注册号
    coowner = CharField(default='')  # 法人代表姓名
    regCapital = CharField(default='')  # 注册资本
    paidCapital = CharField(default='')  # 实收资本
    regaddress = CharField(default='')  # 客户地址
    coStatus = CharField(default='')  # 企业状态
    coType = CharField(default='')  # 公司类型
    shareholders = CharField(default='')  # 股东发起人
    createDate = CharField(default='')  # 成立时间
    businessDate = CharField(default='')  # 经营时间
    regOrg = ForeignKeyField(GsOrg, related_name='regOrgGsorg', null=True)  # 登记机关
    accOrg = ForeignKeyField(GsOrg, related_name='accOrgGsorg', null=True)  # 受理机关
    manOrg = ForeignKeyField(GsOrg, related_name='manOrgGsorg', null=True)  # 管辖机关
    licensingAuthority = ForeignKeyField(GsOrg, related_name='licensingAuthorityGsorg', null=True)  # 发照机关
    businessRange = TextField(default='')  # 经营范围
    stationedPeriod = CharField(default='')  # 驻在期限
    economicNature = CharField(default='')  # 经济性质
    modeOfOperation = CharField(default='')  # 经营方式
    sendCompanyName = CharField(default='')  # 派出企业名称
    registeredForeignEnterprise = CharField(default='')  # 派出企业注册地
    theAgencySetUpDates = CharField(default='')  # 本机构设立日期
    underTheEnterprise = CharField(default='')  # 隶属企业
    businessPremises = CharField(default='')  # 经营场所
    other = CharField(default='')  # 其它企业相关


# 企业网站信息
class Website(BaseModel):
    webId = PrimaryKeyField(unique=True)
    regID = ForeignKeyField(Company, related_name="websiteCompanies")  # 企业信息
    licID = CharField(default='')  # 亮照标识号
    domain = CharField(unique=True)  # 域名,唯一
    ip = CharField(default='')  # ip地址
    isp = CharField(default='')  # isp服务商
    icp = CharField(default='')  # icp注册号
    type = CharField()  # 网站类型
    server_address = CharField(default='')  # 服务器所在地
    name = CharField(default='')  # 网站名称
    memo = CharField(default='')  # 网站描述
    other = CharField(default='')  # 其它内容
    updateDate = DateTimeField()  # 网站亮照的更新时间
    jump = ForeignKeyField('self', related_name='jumps', null=True)  # 跳转路径,自引用
    area = CharField()  # 所属区域


# 亮照信息
class Lz(BaseModel):
    # name=CharField(default='')
    # title=CharField(default='')
    # url=CharField(default='')
    # applyID=BooleanField(default=False)
    # lz=CharField(default='')
    webId = ForeignKeyField(Website, related_name='lzWebs')
    lzId = CharField(unique=True, primary_key=True)
    type = CharField(default='')


# 任务信息
class Task(BaseModel):
    taskId = CharField(unique=True, primary_key=True)  # 任务Id
    userId = ForeignKeyField(Users, related_name='taskUsers')  # 任务的创建人,引用用户表中的用户id
    intervalDay = IntegerField(default=0)  # 间隔时间
    taskType = IntegerField(default=1)  # 任务类型
    packCount = IntegerField()
    state = IntegerField(default=1)  # 任务状态:0.记录未接收完整 1.正在运行 2.已完成 3 – 等待下次巡检 -1 – 任务取消
    missPackId = CharField(default='')
    ctime = DateField(default=datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')) #任务创建时间


# 任务结果
class TaskResult(BaseModel):
    taskResultId = PrimaryKeyField()
    taskId = ForeignKeyField(Task, related_name='taskResults')  # Task表中的taskId
    state = CharField()  #  1 – 正在运行 2 – 完成 3 – 等待下次巡检 -1 – 任务取消
    createTime = DateTimeField(default=datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S'))  # 创建时间
    overTime = DateTimeField()  # 任务的完成时间
    downloadAddress = CharField(default='')  # 任务检查后的结果地址


# 子任务信息
class TaskInfo(BaseModel):
    taskResultId = ForeignKeyField(TaskResult, related_name='taskResults')  # 引用任务表中的taskId
    webId = ForeignKeyField(Website, related_name='taskWebs')  # url地址
    state = CharField(default='')  # 子任务状态  1:已经接收 2:已经亮照 3:未亮照 4：亮照错误 5:亮照页面无法访问 6:已发送（向celery的worker发送任务后） 7:网站首页无法访问 8:公司名称不一致 9：网址不一致 ,-1:抓取异常失败
    remark = CharField(default='')  # 用于存储备注信息


# 亮照结果
class LzResult(BaseModel):
    lzId = ForeignKeyField(Lz, related_name='lzResults')
    result = CharField(default='')  # 亮照结果  已亮照，未亮照，无法访问，亮照错误
    lzDate = DateTimeField(default=datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S'))  # 亮照检查结果时间


# 列类型
class KeyType(BaseModel):
    id = PrimaryKeyField()
    name = CharField(unique=True)


# 列信息
class Keys(BaseModel):
    key = CharField()  # 包含列的关键字
    type = ForeignKeyField(KeyType, related_name='keyTypes')  # 外键，引用列类型主键


# 参数信息配置
class Configs(BaseModel):
    type = CharField()
    expired = IntegerField()  # 更新时间的周期


# 不规则的网址记录
class ErrorWeb(BaseModel):
    url = CharField()
    resultId = ForeignKeyField(LzResult, related_name="resultLzs")



def addKeyType(name):
    if Keys.getOne(key=name) is None:
        psql_db.transaction()
        db = Keys()
        db.key = name
        try:
            db.save(force_insert=True)
            return 1

        except Exception, e:
            print e
            psql_db.rollback()
            return -1
    else:
        return 0


# 添加亮照
def addLz(name='', title='', url='', applyID=False, lz='', org='000000', lzID='', dtype=''):
    if not isinstance(Lz.getOne(name=name, lzID=lzID, url=url), Lz):
        psql_db.transaction()
        db = Lz()
        db.name = name
        db.title = title
        db.url = url
        db.applyID = applyID
        db.lz = lz
        db.org = org
        db.lzID = lzID
        db.dtype = dtype

        try:
            db.save()
            return 1

        except Exception, e:
            print e
            psql_db.rollback()
            return -1

    else:
        return 0


# 新增公司工商信息
def addGsOrg(GsId='', GsName=''):
    if GsId != '' and len(GsId) == 6 and GsName != '':
        psql_db.transaction()
        db = GsOrg()
        save = False
        if not isinstance(GsOrg.getOne(OrgID=GsId, name=GsName), GsOrg):
            # print "This new company"
            save = True
            db.OrgID = GsId
            db.name = GsName
            if GsId[-4:] == u'0000':
                db.upOrg = u'000000'
            else:
                db.upOrg = GsId[:2] + u'0000'
                # print "This company has recorded"
        else:
            pass
        if save:
            try:
                db.save()
                return True
                # print u"公司名称：%s，注册号：%s，处理成功."%(com.coname,com.regID)
            except Exception, e:
                print e
                # print u"公司名称：%s，注册号：%s，处理失败..."%(com.coname,com.regID)
                psql_db.rollback()
                return False
        else:
            print u"名称：%s，编号：%s，已在册." % (db.name, db.OrgID)
            return False


def money(strMoney):
    print "processing money"
    if strMoney.find(u' 万人民币') != -1:
        return float(strMoney[:strMoney.find(u' 万人民币')])


def bsDate(strDate):
    # print "processing date"
    # print strDate
    dt = ''
    # print len(strDate)
    if strDate.find(u'至') != -1:
        # print 'not regular.'
        # print  strDate[strDate.index(u'至')+1:]
        dt = strDate[strDate.index(u'至') + 1:]
    elif len(strDate) == 11:
        # print 'Create date'
        dt = strDate
    elif len(strDate) == 22:
        # print 'no limited'
        pass
    if dt != '':
        import re
        pat = r'\d+'
        results = re.findall(pat, dt)
        # print results
        if results != []:
            y, m, d = results
            y = int(y)
            m = int(m)
            d = int(d)
            return datetime.date(y, m, d)
        else:
            return ''
    else:
        return dt


# 判断是否有亮照
def haslzid(regID):
    if not isinstance(Company.getOne(regID=regID), Company):
        return False
    else:
        return True


# 获取所有关键字类型
def getAllKeyType():
    typeNames = []
    for t in KeyType.select():
        typeNames.append(t.name)
    return typeNames


# 获取所有列信息
def getAllKeys():
    return Keys.select()


# 根据指定的typeId获取字段信息
def getKeysByTypeId(typeId):
    return Keys.select(Keys.type == typeId)


def getKeyNamesByKeyTypeName(typeName):
    return Keys.select().join(KeyType).where(KeyType.name == typeName)


# 通过读取列信息添加公司信息
def addCompanyInfo(co=[]):
    if co != []:
        psql_db.transaction()
        save = False
        regNames = getKeyNamesByKeyTypeName('注册号')
        com = None
        # 获取名称相关
        regid = None
        for regName in regNames:
            for line in co:
                keyName = regName.key
                if line.find(u'' + keyName) != -1:
                    # print line[4:]
                    tempLen = len(keyName) + 1
                    regid = line[tempLen:]
                    if Company.getOne(regID=regid) is None:
                        # print "This new company"
                        save = True
                        break
            if save:
                break
        log = open('../logs/db.log', 'a')
        try:
            if save:
                # 构建需要插入的公司信息
                com = buildCompany(co)
                com.save()
            else:
                print '已经注册：', regid
        except Exception, e:
            print e
            log.write("注册号：%s，处理失败...\n" % (regid))
            print u"注册号：%s，处理失败..." % (regid)
            psql_db.rollback()
        finally:
            if log:
                log.close()
    else:
        print '公司信息为空'


# 导入公司信息
def impCompanyInfo(co):
    if co is not None:
        psql_db.transaction()
        save = False
        if 1 > Company.select().where(Company.regID == co.regID).count():
            save = True
        log = open('./logs/impdb.log', 'a')
        try:
            if save:
                co.save()
            else:
                # 如果已经存在则进行修改
                q = Company.update(coname=co.coname, regID=co.regID, coowner=co.coowner, regCapital=co.regCapital,
                                   paidCapital=co.paidCapital, regaddress=co.regaddress, coStatus=co.coStatus,
                                   coType=co.coType, shareholders=co.shareholders, createDate=co.createDate,
                                   businessDate=co.businessDate, regOrg=co.regOrg, accOrg=co.accOrg,
                                   manOrg=co.manOrg, businessRange=co.businessRange, stationedPeriod=co.stationedPeriod,
                                   licensingAuthority=co.licensingAuthority, economicNature=co.economicNature,
                                   modeOfOperation=co.modeOfOperation, sendCompanyName=co.sendCompanyName,
                                   registeredForeignEnterprise=co.registeredForeignEnterprise,
                                   theAgencySetUpDates=co.theAgencySetUpDates, underTheEnterprise=co.underTheEnterprise,
                                   businessPremises=co.businessPremises, other=co.other).where(
                        Company.regID == co.regID)
                q.execute()
        except Exception, e:
            print e
            log.write("注册号：%s，处理失败...\n" % (co.regID))
            print u"注册号：%s，处理失败..." % (co.regID)
            psql_db.rollback()
        finally:
            if log:
                log.close()
    else:
        print '公司信息为空'


# 根据解析后的字符串信息构建企业对象
def buildCompany(co=[]):
    com = None
    if co != [] and co is not None:
        com = Company()
        allKeys = getAllKeys()
        for line in co:
            for k in allKeys:
                typeName = u'' + k.type.name
                keyName = u'' + k.key
                if line.find(':') != -1:
                    tempArrs = line.split(':')
                    if tempArrs[0].find(keyName) != -1:
                        keyValue = tempArrs[1]
                        # 进行类型匹配
                        if (u'企业名称' == typeName):
                            com.coname = keyValue
                            break
                        elif (u'注册号' == typeName):
                            com.regID = keyValue
                            break
                        elif (u'法人代表姓名' == typeName):
                            com.coowner = keyValue
                            break
                        elif (u'注册资本' == typeName):
                            com.regCapital = keyValue
                            break
                        elif (u'实收资本' == typeName):
                            com.paidCapital = keyValue
                            break
                        elif (u'客户地址' == typeName):
                            com.regaddress = keyValue
                            break
                        elif (u'企业状态' == typeName):
                            com.coStatus = keyValue
                            break
                        elif (u'公司类型' == typeName):
                            com.coType = keyValue
                            break
                        elif (u'股东发起人' == typeName):
                            com.shareholders = keyValue
                            break
                        elif (u'成立时间' == typeName):
                            com.createDate = keyValue
                            break
                        elif (u'经营时间' == typeName):
                            com.businessDate = keyValue
                            break
                        elif (u'登记机关' == typeName):
                            # 根据登记机关的名称查询登记机关对应的id
                            com.regOrg = GsOrg.getOne(GsOrg.name == keyValue)
                            break
                        elif (u'受理机关' == typeName):
                            com.accOrg = GsOrg.getOne(GsOrg.name == keyValue)
                            break
                        elif (u'管辖机关' == typeName):
                            com.manOrg = GsOrg.getOne(GsOrg.name == keyValue)
                            break
                        elif (u'经营范围' == typeName):
                            com.businessRange = keyValue
                            break
                        elif (u'驻在期限' == typeName):
                            com.stationedPeriod = keyValue
                            break
                        elif (u'发照机关' == typeName):
                            com.licensingAuthority = GsOrg.getOne(GsOrg.name == keyValue)
                            # 有发照机关的没有登记机关，默认将登记机关绑定为发照机关
                            # com.regOrg =GsOrg.getOne(GsOrg.name == keyValue)
                            break;
                        elif (u'经济性质' == typeName):
                            com.economicNature = keyValue
                            break
                        elif (u'经营方式' == typeName):
                            com.modeOfOperation = keyValue
                            break
                        elif (u'派出企业名称' == typeName):
                            com.sendCompanyName = keyValue
                            break
                        elif (u'派出企业注册地' == typeName):
                            com.registeredForeignEnterprise = keyValue
                            break
                        elif (u'本机构设立日期' == typeName):
                            com.theAgencySetUpDates = keyValue
                            break
                        elif (u'隶属企业' == typeName):
                            com.underTheEnterprise = keyValue
                            break
                        elif (u'经营场所' == typeName):
                            com.businessPremises = keyValue
                            break
                        else:
                            # 将没有匹配的字段加入其它字段进行存储
                            com.other = line

    return com


# 构建网站信息
def buildWebsite(web=[]):
    if web != [] and web is not None:
        resultWeb = Website()
        for w in web:
            if w.find(':') != -1:
                tempArrs = w.split(':')
                key = tempArrs[0]
                i = w.find(":") + 1
                value = w[i:]
                if (u'亮照标识编号' == key):
                    resultWeb.licID = value
                elif (u'网站名称' == key):
                    resultWeb.name = value
                elif (u'IP地址' == key):
                    resultWeb.ip = value
                elif (u'ISP提供商' == key):
                    resultWeb.isp = value
                elif (u'网站类型' == key):
                    resultWeb.type = value
                elif (u'服务器所在地' == key):
                    resultWeb.server_address = value
                elif (u'域名' == key):
                    resultWeb.domain = value
                else:
                    resultWeb.other = w
        return resultWeb


# 更新或新增网站信息
def impWebsite(web):
    if web is not None:
        psql_db.transaction()
        save = False
        if 1 > Website.select().where(Website.domain== web.domain).count():
            save = True
        try:
            if save:
                web.save()
                print  'url:',web.domain
            else:
                # 如果已经存在则进行修改
                q = Website.update(licID=web.licID, name=web.name, ip=web.ip, isp=web.isp,
                                   type=web.type, server_address=web.server_address, domain=web.domain,
                                   other=web.other, updateDate=web.updateDate).where(
                        Website.domain == web.domain)
                print 'update:', q.execute()
        except Exception, e:
            print e
            psql_db.rollback()
    else:
        print '网站信息为空'


def init_table(tables):
    for table in tables:
        if not table.table_exists():
            print 'Creating table:', str(table)
            psql_db.create_table(table, safe=True)
            print 'Create table success'
        else:
            print 'table is already exists.', str(table)


def drop_table():
    t = tables.reverse()
    for tb in tables:
        if tb.table_exists():
            tb.drop_table()


def create_user():
    u = Users.getOne(Users.userName == 'admin')
    if u == None or (not isinstance(u, Users)):
        print 'not found admin user'
        r = Users(userName='admin', userPwd='admin', userRole='admin')
        result = r.save()
        if result == 1:
            print 'user created success'
        else:
            print 'user created fail'


def createKeyType(value):
    if KeyType.getOne(name=value) is None:
        r = KeyType(name=value)
        result = r.save()
        if result == 1:
            print 'keyType记录插入成功'
        else:
            print 'keyType记录插入失败'


# 新建任务
def addTask(str, users, interval):
    result = None
    if str != '':
        t = Task()
        t.taskId = str
        t.userId = users
        t.intervalDay = interval
        result = t.save(force_insert=True)
    return result


def insertRecordToKeyType():
    values = ['企业名称', '注册号', '法人代表姓名', '注册资本', '实收资本', '客户地址',
              '企业状态', '公司类型', '股东发起人', '成立时间', '经营时间', '登记机关',
              '受理机关', '管辖机关', '经营范围', '驻在期限', '发照机关', '经济性质',
              '经营方式', '派出企业名称', '派出企业注册地', '本机构设立日期', '隶属企业'
        , '亮照标示号', '域名', 'IP地址', 'isp服务商', 'icp注册号', '网站类型', '服务器地址',
              '网站名称', '网站描述', '亮照类型', '经营场所', '其它']
    # 新增列类型数据
    for v in values:
        createKeyType(v)





        # 创建用户
        # create_user()










        # if False:
        #     print "Droping tables..."
        #     for table in tables:
        #         table.drop_table()
        #     print 'All cleared.'
        # if True:
        #
        #     print "Initing tables in Database..."
        #     for table in tables:
        #         if not table.table_exists():
        #             print "Creating table:",str(table)
        #             psql_db.create_table(table,safe=True)
        #             print "Success."
        #         else:
        #             print "Table",str(table)," has found."
        #
        #     #r=Users.getOne('admin') #检测是否有admin
        #     r=Users.getOne(user_id='admin')
        #     if r == None or (not isinstance(r,Users)):
        #         print "Not found admin user."
        #         print "Creating admin..."
        #         r= Users(user_id='admin',user_pwd='admin',user_role='administrator') #创建初始admin用户
        #         r.save()
        #         print "Success."
        #     else:
        #         print "admin found."
        # if False:
        #     one=[u'\u540d\u79f0:\u4e0a\u6d77\u5e7f\u8c31\u745e\u533b\u7597\u79d1\u6280\u6709\u9650\u516c\u53f8', u'\u6ce8\u518c\u53f7:310115002632028', u'\u6cd5\u5b9a\u4ee3\u8868\u4eba\u59d3\u540d:\u5b59\u5929\u4f1f', u'\u4f4f\u6240:\u4e0a\u6d77\u5e02\u5f20\u6c5f\u9ad8\u79d1\u6280\u56ed\u533a\u5f20\u8861\u8def666\u5f042\u53f7207\u5ba4', u'\u6ce8\u518c\u8d44\u672c:500.000000\xa0\u4e07\u4eba\u6c11\u5e01', u'\u4f01\u4e1a\u72b6\u6001:\u786e\u7acb', u'\u516c\u53f8\u7c7b\u578b:\u6709\u9650\u8d23\u4efb\u516c\u53f8(\u56fd\u5185\u5408\u8d44)', u'\u6210\u7acb\u65e5\u671f:2015\u5e7404\u670807\u65e5', u'\u8425\u4e1a\u671f\u9650:2015\u5e7404\u670807\u65e5\xa0\u81f32045\u5e7404\u670806\u65e5', u'\u767b\u8bb0\u673a\u5173:\u81ea\u8d38\u8bd5\u9a8c\u533a\u5206\u5c40', u'\u53d7\u7406\u673a\u5173:\u81ea\u8d38\u8bd5\u9a8c\u533a\u5206\u5c40', u'\u7ecf\u8425\u8303\u56f4:\u533b\u7597\u79d1\u6280\u3001\u8ba1\u7b97\u673a\u8f6f\u786c\u4ef6\u3001\u7f8e\u5bb9\u4eea\u5668\u9886\u57df\u5185\u7684\u6280\u672f\u5f00\u53d1\u3001\u6280\u672f\u54a8\u8be2\u3001\u6280\u672f\u670d\u52a1\uff0c\u533b\u7597\u5668\u68b0\u3001\u7535\u5b50\u4ea7\u54c1\u3001\u5316\u5986\u54c1\u7684\u9500\u552e\uff0c\u4ece\u4e8b\u8d27\u7269\u4e0e\u6280\u672f\u7684\u8fdb\u51fa\u53e3\u4e1a\u52a1\u3002\u3010\u4f9d\u6cd5\u987b\u7ecf\u6279\u51c6\u7684\u9879\u76ee\uff0c\u7ecf\u76f8\u5173\u90e8\u95e8\u6279\u51c6\u540e\u65b9\u53ef\u5f00\u5c55\u7ecf\u8425\u6d3b\u52a8\u3011']
        #     addCompany(one)
        #     two=[u'\u540d\u79f0:\u4f17\u7269\uff08\u4e0a\u6d77\uff09\u79d1\u6280\u6709\u9650\u516c\u53f8', u'\u6ce8\u518c\u53f7:310115002463983', u'\u6cd5\u5b9a\u4ee3\u8868\u4eba\u59d3\u540d:\u6797\u4f1f', u'\u4f4f\u6240:\u4e2d\u56fd\uff08\u4e0a\u6d77\uff09\u81ea\u7531\u8d38\u6613\u8bd5\u9a8c\u533a\u76db\u590f\u8def570\u53f71206-E\u5ba4', u'\u6ce8\u518c\u8d44\u672c:250.000000\xa0\u4e07\u4eba\u6c11\u5e01', u'\u4f01\u4e1a\u72b6\u6001:\u786e\u7acb', u'\u516c\u53f8\u7c7b\u578b:\u6709\u9650\u8d23\u4efb\u516c\u53f8(\u56fd\u5185\u5408\u8d44)', u'\u6210\u7acb\u65e5\u671f:2014\u5e7410\u670822\u65e5', u'\u8425\u4e1a\u671f\u9650:2014\u5e7410\u670822\u65e5\xa0\u81f3', u'\u767b\u8bb0\u673a\u5173:\u81ea\u8d38\u8bd5\u9a8c\u533a\u5206\u5c40', u'\u53d7\u7406\u673a\u5173:\u81ea\u8d38\u8bd5\u9a8c\u533a\u5206\u5c40', u'\u7ecf\u8425\u8303\u56f4:\u79fb\u52a8\u901a\u4fe1\u3001\u7269\u8054\u7f51\u3001\u8ba1\u7b97\u673a\u8f6f\u4ef6\u9886\u57df\u5185\u7684\u6280\u672f\u54a8\u8be2\u3001\u6280\u672f\u670d\u52a1\u3001\u6280\u672f\u8f6c\u8ba9\uff0c\u8ba1\u7b97\u673a\u8f6f\u4ef6\u7684\u5236\u4f5c\u3001\u9500\u552e\uff0c\u8ba1\u7b97\u673a\u786c\u4ef6\u53ca\u8017\u6750\u3001\u901a\u4fe1\u8bbe\u5907\u53ca\u4ea7\u54c1\u3001\u7535\u5b50\u4ea7\u54c1\u7684\u9500\u552e\uff0c\u7cfb\u7edf\u96c6\u6210\uff0c\u5e7f\u544a\u7684\u8bbe\u8ba1\u3001\u5236\u4f5c\u3001\u4ee3\u7406\uff0c\u5229\u7528\u81ea\u6709\u5a92\u4f53\u53d1\u5e03\uff0c\u5e02\u573a\u4fe1\u606f\u54a8\u8be2\u4e0e\u8c03\u67e5\uff08\u4e0d\u5f97\u4ece\u4e8b\u793e\u4f1a\u8c03\u67e5\u3001\u793e\u4f1a\u8c03\u7814\u3001\u6c11\u610f\u8c03\u67e5\u3001\u6c11\u610f\u6d4b\u9a8c\uff09\uff0c\u4f01\u4e1a\u8425\u9500\u7b56\u5212\uff0c\u4f01\u4e1a\u7ba1\u7406\u54a8\u8be2\uff0c\u6295\u8d44\u7ba1\u7406\u3002\u3010\u4f9d\u6cd5\u987b\u7ecf\u6279\u51c6\u7684\u9879\u76ee\uff0c\u7ecf\u76f8\u5173\u90e8\u95e8\u6279\u51c6\u540e\u65b9\u53ef\u5f00\u5c55\u7ecf\u8425\u6d3b\u52a8\u3011']
        #     addCompany(two)


if __name__ == '__main__':
    # tables=[Users,GsOrg,Company,Website,Lz,Task,TaskInfo,LzResult,TaskResult]
    # tables = [Users, GsOrg, Company, Website, Lz, Task, TaskInfo, LzResult, TaskResult]
    tables = [ErrorWeb]
    # 删除表
    # drop_table();

    # 创建表
    init_table(tables)

    # 新增列类型表中的数据
    # insertRecordToKeyType()

    # types = getAllKeyType()
    # for t in types:
    #     print t.id
    # keys  = getAllKeys()
    # for k in keys:
    #     ktype =  k.type
    #     # print 'type:',ktype.name
    #     # print k.key
    #     print ktype.name


    # keyNames = getKeyNamesByKeyTypeName('企业名称')
    # print len(list(keyNames))
    # for name in keyNames:
    #     print name.key


    # line=[u'\u540d\u79f0:\u4e0a\u6d77\u5e7f\u8c31\u745e\u533b\u7597\u79d1\u6280\u6709\u9650\u516c\u53f8', u'\u6ce8\u518c\u53f7:310115002632028', u'\u6cd5\u5b9a\u4ee3\u8868\u4eba\u59d3\u540d:\u5b59\u5929\u4f1f', u'\u4f4f\u6240:\u4e0a\u6d77\u5e02\u5f20\u6c5f\u9ad8\u79d1\u6280\u56ed\u533a\u5f20\u8861\u8def666\u5f042\u53f7207\u5ba4', u'\u6ce8\u518c\u8d44\u672c:500.000000\xa0\u4e07\u4eba\u6c11\u5e01', u'\u4f01\u4e1a\u72b6\u6001:\u786e\u7acb', u'\u516c\u53f8\u7c7b\u578b:\u6709\u9650\u8d23\u4efb\u516c\u53f8(\u56fd\u5185\u5408\u8d44)', u'\u6210\u7acb\u65e5\u671f:2015\u5e7404\u670807\u65e5', u'\u8425\u4e1a\u671f\u9650:2015\u5e7404\u670807\u65e5\xa0\u81f32045\u5e7404\u670806\u65e5', u'\u767b\u8bb0\u673a\u5173:\u81ea\u8d38\u8bd5\u9a8c\u533a\u5206\u5c40', u'\u53d7\u7406\u673a\u5173:\u81ea\u8d38\u8bd5\u9a8c\u533a\u5206\u5c40', u'\u7ecf\u8425\u8303\u56f4:\u533b\u7597\u79d1\u6280\u3001\u8ba1\u7b97\u673a\u8f6f\u786c\u4ef6\u3001\u7f8e\u5bb9\u4eea\u5668\u9886\u57df\u5185\u7684\u6280\u672f\u5f00\u53d1\u3001\u6280\u672f\u54a8\u8be2\u3001\u6280\u672f\u670d\u52a1\uff0c\u533b\u7597\u5668\u68b0\u3001\u7535\u5b50\u4ea7\u54c1\u3001\u5316\u5986\u54c1\u7684\u9500\u552e\uff0c\u4ece\u4e8b\u8d27\u7269\u4e0e\u6280\u672f\u7684\u8fdb\u51fa\u53e3\u4e1a\u52a1\u3002\u3010\u4f9d\u6cd5\u987b\u7ecf\u6279\u51c6\u7684\u9879\u76ee\uff0c\u7ecf\u76f8\u5173\u90e8\u95e8\u6279\u51c6\u540e\u65b9\u53ef\u5f00\u5c55\u7ecf\u8425\u6d3b\u52a8\u3011']
    #
    # com = buildCompany(line)
    # print com.shareholders


    # f = None
    # try:
    #     dataFile = file('../logs/data.txt')
    #     os.remove(dataFile)
    #     f = open('../logs/data.txt', 'a')
    #     for c in companies:
    #         f.write(''.join(c) + '\r\n')
    #     f.flush()
    # except Exception, e:
    #     print e
    # finally:
    #     if f and f.closed is not True:
    #         f.close()
    # 添加公司信息
    # companyPath = '/home/bwh/tmp/gslz/nlz'
    # companies = parseHtmlFiles(companyPath)
    # print 'length:', len(companies)
    # for co in companies:
    #     addCompanyInfo(co)
    #
    # print '添加公司信息完成'




    # print com.regOrg.name




    # keyType = KeyType.select()
    # for kt in keyType:
    #     print kt.id
