# _*_coding: UTF-8_*_
import datetime

from peewee import *

import config


#初始化postgresql数据库
psql_db = PostgresqlDatabase(config.dbName,user = config.dbUser,password=config.dbPWD,host = config.dbIP)


#base
class BaseModel(Model):
    class Meta:
        database = psql_db


    @classmethod
    def getOne(cls,*query,**kwargs):
        try:
            return cls.get(*query,**kwargs)
        except DoesNotExist:
            return None


#Users
class Users(BaseModel):
    userId = PrimaryKeyField(unique=True)
    userName = CharField(max_length=50,unique=True)
    userPwd = CharField(max_length=50)
    userRole = CharField(default='Normal',max_length=50)
    createDate = DateTimeField(default=datetime.datetime.now)


#工商信息
class GsOrg(BaseModel):#工商
    name = CharField(default='') #机关名称
    orgID= CharField(primary_key=True,default='') #原始机关编号
    upOrg = CharField(default='000000') #上级机关
    address = CharField(default='') #机关地址
    tel = CharField(default='') #机关电话


#企业基本信息
class Company(BaseModel):
    coname = CharField(default='') # 企业名称
    regID = CharField(unique=True) #注册号
    coowner = CharField() #法人代表姓名
    regCapital = CharField(default='') #注册资本
    paidCapital = CharField(default='') #实收资本
    regaddress = CharField(default='') #客户地址
    coStatus = CharField(default='')#企业状态
    coType = CharField(default='') #公司类型
    shareholders = CharField(default='') #股东发起人
    createDate = CharField() #成立时间
    businessDate = CharField() #经营时间
    regOrg = ForeignKeyField(GsOrg,related_name='gsorgCompanies') #登记机关
    accOrg = CharField(default='') #受理机关
    manOrg = CharField(default='') #管辖机关
    businessRange = TextField(default='') #经营范围
    stationedPeriod = CharField(default='') #驻在期限
    licensingAuthority = CharField(default='')  #发照机关
    economicNature = CharField(default='')   #经济性质
    modeOfOperation = CharField(default='') #经营方式
    sendCompanyName = CharField(default='')  #派出企业名称
    registeredForeignEnterprise = CharField(default='') #派出企业注册地
    theAgencySetUpDates = CharField(default='')  #本机构设立日期
    underTheEnterprise = CharField(default='') #隶属企业
    businessPremises = CharField(default='')  #企业场所




#企业网站信息
class Website(BaseModel):
    webId = PrimaryKeyField(unique=True)
    regID = ForeignKeyField(Company,related_name="websiteCompanies") #企业信息
    licID = CharField() #亮照标示号
    domain = CharField() #域名
    ip = CharField() #ip地址
    isp = CharField() #isp服务商
    icp = CharField() #icp注册号
    type = CharField() #网站类型
    server_address =CharField() #服务器地址
    name = CharField() #网站名称
    memo = CharField() #网站描述


#亮照信息
class Lz(BaseModel):
    webId = ForeignKeyField(Website,related_name ='lzWebs')
    lzId=CharField(unique=True,primary_key=True)
    type=CharField(default='') #亮照类型



#任务信息
class Task(BaseModel):
    taskId = CharField(unique=True,primary_key=True) #任务Id
    userId = ForeignKeyField(Users,related_name='taskUsers') #任务的创建人,引用用户表中的用户id
    intervalDay = CharField() #间隔时间

#子任务信息
class TaskInfo(BaseModel):
    subTaskId = CharField(unique=True,primary_key=True)  #子任务Id
    taskId = ForeignKeyField(Task,related_name='taskInfoTasks')  #引用任务表中的taskId
    webId = ForeignKeyField(Website,related_name='taskWebs')  #url地址
    state = CharField() #子任务状态


#任务结果
class TaskResult(BaseModel):
    taskId = ForeignKeyField(Task,related_name='taskResults') #Task表中的taskId
    state = CharField()  #任务的执行状态
    mail = CharField()  #通知邮箱地址
    createTime = DateTimeField(default='') #创建时间
    overTime = DateTimeField() #任务的完成时间
    downloadAddress = CharField(default='') #任务检查后的结果地址


#亮照结果
class LzResult(BaseModel):
    lzId=ForeignKeyField(Lz,related_name='lzResults')
    result = CharField(default='')  #亮照结果  已亮照，未亮照，无法访问，亮照错误
    lzDate = DateTimeField() #亮照检查结果时间


#列类型
class KeyType(BaseModel):
    id = PrimaryKeyField()
    name = CharField(unique=True)


#列信息
class Keys(BaseModel):
    key = CharField() #包含列的关键字
    type = ForeignKeyField(KeyType,related_name='keyTypes')  #外键，引用列类型主键





def addKeys(name):
    if not isinstance(Keys.getOne(key=name),Keys):
        psql_db.transaction()
        db = Keys()
        db.key = name
        try:
            db.save()
            return 1

        except Exception,e:
            print e
            psql_db.rollback()
            return -1
    else:
        return 0




#添加亮照
def addLz(org,lzID,dtype,name):

    if not isinstance(Lz.getOne(name=name,lzID=lzID),Lz):
        psql_db.transaction()
        db=Lz()
        db.org=org
        db.lzID=lzID
        db.dtype=dtype

        try:
            db.save()
            return 1

        except Exception,e:
            print e
            psql_db.rollback()
            return -1
    else:
        return 0


#新增公司工商信息
def addGsOrg(GsId='',GsName=''):

    if GsId!='' and len(GsId)==6 and GsName!='':
        psql_db.transaction()
        db=GsOrg()
        save=False
        if not isinstance(GsOrg.getOne(OrgID=GsId,name=GsName),GsOrg):
            # print "This new company"
            save=True
            db.OrgID=GsId
            db.name=GsName
            if GsId[-4:]==u'0000':
                db.upOrg=u'000000'
            else:
                db.upOrg=GsId[:2]+u'0000'
            # print "This company has recorded"
        else:
            pass
        if save:
            try:
                db.save()
                return True
                #print u"公司名称：%s，注册号：%s，处理成功."%(com.coname,com.regID)
            except Exception,e:
                print e
                #print u"公司名称：%s，注册号：%s，处理失败..."%(com.coname,com.regID)
                psql_db.rollback()
                return False
        else:
            print u"名称：%s，编号：%s，已在册."%(db.name,db.OrgID)
            return False

def bsDate(strDate):
    #print "processing date"
    #print strDate
    dt=''
    #print len(strDate)
    if strDate.find(u'至')!=-1:
        # print 'not regular.'
        #print  strDate[strDate.index(u'至')+1:]
        dt= strDate[strDate.index(u'至')+1:]
    elif len(strDate)==11:
        # print 'Create date'
        dt= strDate
    elif len(strDate)==22:
        # print 'no limited'
        pass
    if dt!='':
        import re
        pat = r'\d+'
        results = re.findall(pat,dt)
        #print results
        if results!=[]:
            y,m,d=results
            y=int(y)
            m=int(m)
            d=int(d)
            return datetime.date(y,m,d)
        else:return ''
    else:
        return dt



#添加公司信息
def addCompany(co=[]):

    if co!=[]:
        psql_db.transaction()
        com=Company()
        save=False
        for line in co:
            if line.find(u'名称:')!=-1:
                # print line[3:]
                com.coname=line[3:]
            elif line.find(u'注册号:')!=-1:
                # print line[4:]
                if not isinstance(Company.getOne(regID=line[4:]),Company):
                    # print "This new company"
                    save=True
                else:
                    pass
                    # print "This company has recorded"

                com.regID=line[4:]
            elif line.find(u'法定代表人姓名:')!=-1 :
                # print line[8:]
                com.coowner=line[8:]
            elif line.find(u'法定代表人:')!=-1 :
                # print line[8:]
                com.coowner=line[8:]
            elif line.find(u'住所:')!=-1:
                # print line[3:]
                com.regaddress=line[3:]
            elif line.find(u'注册资本:')!=-1:
                # print line[5:]
                com.regCapital=line[5:]
            elif line.find(u'企业状态:')!=-1:
                # print line[5:]
                com.coStatus=line[5:]
            elif line.find(u'公司类型:')!=-1:
                # print line[5:]
                com.coType=line[5:]
            elif line.find(u'成立日期:')!=-1:
                # print line[5:]
                com.CreateDate=bsDate(line[5:])
            elif line.find(u'营业期限:')!=-1:
                # print line[5:]
                com.BusinessDate=bsDate(line[5:])
            elif line.find(u'登记机关:')!=-1:
                # print line[5:]
                com.RegOrg=line[5:]
            elif line.find(u'受理机关:')!=-1:
                # print line[5:]
                com.AccOrg=line[5:]
            elif line.find(u'经营范围:')!=-1:
                # print line[5:]
                com.BusinessRange=line[5:]

        if save:
            try:
                com.save()
                print u"公司名称：%s，注册号：%s，处理成功."%(com.coname,com.regID)
            except Exception,e:
                print e
                print u"公司名称：%s，注册号：%s，处理失败..."%(com.coname,com.regID)
                psql_db.rollback()
        else:
            print u"公司名称：%s，注册号：%s，已在册."%(com.coname,com.regID)







