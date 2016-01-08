# -*- coding:utf-8 -*- 

__author__ = 'xhp'

from bs4 import BeautifulSoup

import db

file=open(u"data/市局/工商所.html",'r')

doc=file.read()

soup=BeautifulSoup(doc,'html.parser')

for item in soup.find_all('option'):
    if item.attrs['value']!='':

        if db.addGsOrg(GsId=item.attrs['value'],\
                GsName=item.text.replace('\t','').\
        replace('\n','').replace(' ','').replace('\r','')):
            print u"发现工商单位：%s，编号：%s。\n添加成功。"%(item.attrs['value'],item.text.replace('\t','')\
            .replace('\n','').\
            replace(' ','').\
            replace('\r',''))
        else:
            print u"发现工商单位：%s，编号：%s。\n添加失败。"%(item.attrs['value'],item.text.replace('\t','')\
            .replace('\n','').\
            replace(' ','').\
            replace('\r',''))