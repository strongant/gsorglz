# _*_coding: UTF-8_*_
from scripts.db import impCompanyInfo, buildCompany
from scripts.impdb import parsePage, TempLz



#检查直到没有新的记录插入为止
from scripts.lzParser import parser


def impData():
    while(parsePage()!=[]):
        companyData = parsePage()
        for data in companyData:
            #解析当前内容
            result = parser(data)
            com = buildCompany(result)
            impCompanyInfo(com)
    data = TempLz.select().where(TempLz.lzID=='20120323163520958')
    for d in data:
        result = parser(d.lzpage)
        for r in result:
            print r


if __name__=='__main__':
    #迁移数据
    impData()




