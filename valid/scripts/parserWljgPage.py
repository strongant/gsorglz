# -*- coding:utf-8 -*-


__author__ = 'xhp'

import os

from bs4 import BeautifulSoup

import db

pags=[{'path':"/Users/xhp/PycharmProjects/htmlParser/data/市局/交易类",'type':'交易类'},\
      {'path':"/Users/xhp/PycharmProjects/htmlParser/data/市局/信息类",'type':'信息类'},\
      {'path':"/Users/xhp/PycharmProjects/htmlParser/data/市局/交易兼信息",'type':'交易兼信息'},\
      {'path':"/Users/xhp/PycharmProjects/htmlParser/data/市局/其他",'type':'其他'}
      ]

# pags=[
#       {'path':"/Users/xhp/PycharmProjects/htmlParser/data/市局/信息类/ls",'type':'信息类'}\
#
#       ]



def process(rootpath,pagetype):
    #cos=[]
    for parent,dirname,filename in os.walk(rootpath):
        for f in filename:
            if f[:1]!='.':
                print os.path.join(parent,f),pagetype
                out=open('./log/%s.log'%os.path.join(parent,f).replace('/','_'),'w')
                if True:
                    file=open(os.path.join(parent,f),'r')
                    doc=file.read()
                    soup=BeautifulSoup(doc,'html.parser')
                    #print soup.table['class']
                    #out=open('./query.txt','w')
                    for table in soup.find_all('table'):
                        if table.attrs['class'][0]=='table_list':
                            #table=soup.table
                            #print table.tbody.tr
                            try:
                                for tr in table.tbody.find_all('tr'):
                                    if False:
                                        for item in tr.find_all('th'):
                                            #print type(item.text)
                                            if not item.find_all('div'):
                                                # print item.text.replace('\t','').replace('\n','').replace(' ','').replace('\r','')
                                                pass
                                    #print tr.find_all('td')
                                    if True:
                                        tmp=[]
                                        for item in tr.find_all('td'):

                                            if not item.find_all('div'):
                                                #if item.a.find('javaScript:entyDetail'):
                                                aitem=item.find_all('a')
                                                if  aitem<>[]:
                                                    href=aitem[0]['href']
                                                    if href.find('javaScript:entyDetail')<>-1:
                                                        lzid=href[href.find('javaScript:entyDetail')+len("javaScript:entyDetail('"):-3]
                                                        #print lzid
                                                        tmp.append(lzid)
                                                if item.attrs.has_key('title'):
                                                    #print item['title']
                                                    tmp.append(item['title'])
                                                    #print text+' added.'
                                                    pass
                                                else:
                                                    text=item.text.replace('\t','').replace('\n','').replace(' ','').replace('\r','')
                                                    #print text
                                                    tmp.append(text)
                                                    #print text+' added.'
                                        #print tmp
                                        tmp.append(pagetype)
                                        applyID=False
                                        #print len(tmp)
                                        #for i in tmp:
                                            #print i

                                        if len(tmp)==9:
                                            #print "found a record."
                                            if tmp[5] ==u'是':
                                                applyID=True
                                            result=db.addTempLz(name=tmp[2],title=tmp[3],url=tmp[4],applyID=applyID,lz=tmp[6],org=tmp[7],lzID=tmp[1],dtype=tmp[8])
                                            if result==1:
                                                pass
                                                #print tmp[4]+' has added.'
                                            elif result==-1:
                                                print tmp[4]+' failed.'
                                                out.write(str(tmp)+'\n')
                                                out.flush()
                                            elif result==0:
                                                print tmp[4]+' found in db.'
                                        else:
                                            out.write(str(tmp)+'\n')
                                            out.flush()
                            except Exception,e:
                                print e
                                print os.path.join(parent,f)+' has error.'
                print "The file done."
                out.close()
                                    #cos.append(tmp)

                #out.close()



if __name__ == '__main__':
    for item in pags:

        process(rootpath=item['path'],pagetype=item['type'])
            # applyID=False
            # #print len(tmp)
            # #for i in tmp:
            #     #print i
            # out=open('./log.txt','w')
            # if len(tmp)==8:
            #     if tmp[5] ==u'是':
            #         applyID=True
            #     result=db.addTempLz(name=tmp[2],title=tmp[3],url=tmp[4],applyID=applyID,lz=tmp[6],org=tmp[7],lzID=tmp[1])
            #     if result==1:
            #         print tmp[4]+' has added.'
            #     elif result==-1:
            #         print tmp[4]+' failed.'
            #         out.write(str(tmp)+'\n')
            #         out.flush()
            #     elif result==0:
            #         print tmp[4]+' found in db.'
            # else:
            #     out.write(str(tmp)+'\n')
            #     out.flush()
            # out.close()