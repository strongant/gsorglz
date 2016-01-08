# -*- coding:utf-8 -*-

__author__ = 'xhp'

import time

from bs4 import BeautifulSoup

import db
import lzParser

lzlst=[]
file=open(u"data/other.html",'r')
doc=file.read()
soup=BeautifulSoup(doc,'html.parser')
#print soup.table['class']
out=open('./query.txt','w')
if soup.table['class'][0]=='table_list':
    table=soup.table
    #print table.tbody.tr
    for tr in table.tbody.find_all('tr'):
        if False:
            for item in tr.find_all('th'):
                #print type(item.text)
                if not item.find_all('div'):
                    # print item.text.replace('\t','').replace('\n','').replace(' ','').replace('\r','')
                    pass
        #print tr.find_all('td')
        if True:
            for item in tr.find_all('td'):
                if not item.find_all('div'):
                    #if item.a.find('javaScript:entyDetail'):
                    aitem=item.find_all('a')
                    if  aitem<>[]:
                        href=aitem[0]['href']
                        if href.find('javaScript:entyDetail')<>-1:
                            lzid=href[href.find('javaScript:entyDetail')+len("javaScript:entyDetail('"):-3]
                            print lzid
                            lzlst.append(lzid)
                            try:

                                if  True:
                                    r=lzParser.parser(lzid)
                                    for line in  r:
                                        out.write(line.encode('utf8')+'\n')
                                        #print line
                                    #print "=============\n"
                                    out.write("=============\n")
                                    out.flush()
                                    db.addCompany(r)
                                else:
                                    print 'this id has recorded.'
                            except Exception,e:
                                print e

                            time.sleep(5)

                    if item.attrs.has_key('title'):
                        #print item['title']
                        pass
                    else:
                        text=item.text.replace('\t','').replace('\n','').replace(' ','').replace('\r','')
                        if text<>'':
                            #print text
                            pass
out.close()





