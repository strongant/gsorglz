# _*_coding: UTF-8_*_
import math

from peewee import PostgresqlDatabase, Model, DoesNotExist, CharField, BooleanField, DateField, TextField

import config
# 初始化目标对象数据库
from scripts.db import buildCompany, impCompanyInfo, buildWebsite, Company, impWebsite
from scripts.lzParser import parser, parserCompanyAndWeb

psql_db = PostgresqlDatabase(config.impDbName, user=config.impDbUser, password=config.ImpDbPWD,
                             host=config.impDbIP)


class BaseModel(Model):
    class Meta:
        database = psql_db

    @classmethod
    def getOne(cls, *query, **kwargs):
        try:
            return cls.get(*query, **kwargs)
        except DoesNotExist:
            return None


class TempLz(BaseModel):
    name = CharField(default='')
    title = CharField(default='')
    url = CharField(default='')
    applyID = BooleanField(default=False)
    lz = CharField(default='')
    org = CharField(default='')
    lzID = CharField(default='')
    dtype = CharField(default='')
    checktime = DateField(default='')
    lzpage = TextField(default='')


# 获取当前所有的亮照信息
def parsePage():
    # 将已经解析过的亮照id写入impdbdata.log
    # 读取impdbdata.log

    log = None
    try:
        # 直到所有页面抓取完毕为止
        while (True):
            f = open('../logs/impdbdata.log', 'r')
            lines = f.readlines()
            arrs = []
            for l in lines:
                arrs.append(l)
            f.close()

            log = open('../logs/impdbdata.log', 'a')
            # 获取此文件中的所有regID
            if arrs != []:
                lzs = TempLz.select().where(
                        (TempLz.lzpage != '')
                        & (TempLz.lzID.not_in(arrs))
                )
                print 'result count:', TempLz.select().where(
                        (TempLz.lzpage != '')
                        & (TempLz.lzID.not_in(arrs))).count()

            else:
                lzs = TempLz.select().where(
                        (TempLz.lzpage != '')
                )
            i = 0
            for lz in lzs:
                i += 1
                result = parser(lz.lzpage)
                com = buildCompany(result)
                # 构建公司信息
                impCompanyInfo(com)
                log.write(lz.lzID + '\n')
                log.flush()
    except Exception, e:
        print e
    finally:
        if log and log.closed is not True:
            log.close()


# 解析所有的网站信息
def parseWebsite():
    log = open('../logs/parseweb.log', 'a')
    # 每次取5000条
    count = TempLz.select().count()
    pagesize = 5000
    pagecount = int(math.ceil(float(count) / float(pagesize)))
    for i in range(pagecount):
        datas = TempLz.select().where(TempLz.id>18879).order_by(TempLz.id).paginate(i + 1, pagesize)
        if datas is not None:
            for d in datas:
                data = d.lzpage
                if data is not None:
                    parseData = parserCompanyAndWeb(data)
                    com = buildCompany(parseData['company'])
                    web = buildWebsite(parseData['web'])
                    if com is not None and web is not None:
                        c = Company.getOne(Company.coname == com.coname)
                        if c is not None:
                            web.regID = c
                            impWebsite(web)
                        else:
                            impCompanyInfo(com)
                            tempCom = Company.getOne(Company.regID == com.regID)
                            web.regID = tempCom
                            impWebsite(web)
                log.write(str(d.id)+ "\n")
                print d.id
    log.flush()
    log.close()


if __name__ == '__main__':
    # count =TempLz.select().where(TempLz.lzpage!='').count()
    # print count
    # lz = TempLz.get(TempLz.lzID == '20120323163520958')
    # data = parser(lz.lzpage)
    # print data
    #
    # for d in data:
    #     print d
    # parsePage()
    # print TempLz.select().where(TempLz.lzpage.is_null()).count()==0

    # lzpage = TempLz.getOne(TempLz.id==1).lzpage
    # c = TempLz.select(fn.Count(fn.Distinct(TempLz.name))).scalar()
    #TempLz.select().where(TempLz.lzpage.is_null(False)).order_by(TempLz.id).paginate(1, 10)
    #parseWebsite()
    # lzpage = TempLz.select().where(TempLz.name=="上海昊锌科技有限公司")
    # for l in lzpage:
    #     page = l.lzpage
    #     parseData = parserCompanyAndWeb(page)
    #     w =  buildWebsite(parseData['web'])
    #     print parseData['web']
    # str = u'\u57df\u540d:http://www.haoxinkj.com/'
    #
    # arrs = str.split(':')

    # str = u'\u57df\u540d:http://www.haoxinkj.com/'
    # i = str.find(":")+1
    #
    # print str[i:]
    templz = TempLz.getOne(TempLz.id==5512)
    lzpage = templz.lzpage
    parseData = parserCompanyAndWeb(lzpage)
    web = parseData.get('web')
    tw = buildWebsite(web)





