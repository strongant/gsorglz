# -*- coding:utf-8 -*-
from util.myPageUtil import stringQ2B

__author__ = 'xhp'

from bs4 import BeautifulSoup
import mycurl
import os


def parserWeb(lzid=''):
    if lzid != '':
        web = mycurl.getLZ(lzid)
        h = open('./lz/%s.html' % lzid, 'w')
        h.write(web)
        h.close()
        return parser(web)


def parserFile(filepath):
    try:
        data = open(filepath, 'r')
        return parser(data)
    except IOError:
        return []
#一次行解析公司信息和网站信息
def parserAllFile(filepath):
    try:
        data = open(filepath, 'r')
        return parserCompanyAndWeb(data)
    except IOError:
        return []


# 解析网站信息
def parserWebSite(filepath):
    try:
        data = open(filepath, 'r')
        return parserWeb(data)
    except IOError:
        return []


def parserFiles(rootdir, ext='html'):
    results = []
    for parent, dirname, filename in os.walk(rootdir):
        for f in filename:
            if filename[-4:] == ext:
                results.append(parserFile(os.path.join(parent, f)))
    return results


def parserFilesByPath(path):
    results = []
    htmlDir = file(path, 'rw')

    return results


# 获取指定路径下所有指定后缀的文件
# dir 指定路径
# ext 指定后缀，链表&不需要带点 或者不指定。例子：['xml', 'java']
def GetFileFromThisRootDir(dir, ext=None):
    allfiles = []
    needExtFilter = (ext != None)
    for root, dirs, files in os.walk(dir):
        for filespath in files:
            filepath = os.path.join(root, filespath)
            extension = os.path.splitext(filepath)[1][1:]
            if needExtFilter and extension in ext:
                allfiles.append(filepath)
            elif not needExtFilter:
                allfiles.append(filepath)
    return allfiles


def parser(data=''):
    if data != '':

        soup = BeautifulSoup(data, 'html.parser')
        # print soup.title.text
        for table in soup.find_all('table'):
            if table.attrs.has_key('id'):
                # print table.attrs['id']
                if table.attrs['id'] == 'resultTbInfo':
                    for sub_table in table.find_all('table'):
                        if sub_table.attrs.has_key('class'):
                            # print sub_table.attrs['class']
                            if sub_table.attrs['class'] == [u'list_boder']:
                                # print sub_table
                                lst = []
                                i = 0
                                for item in sub_table.find_all('td'):
                                    i += 1
                                    line = item.text.replace('\t', '') \
                                        .replace('\n', '') \
                                        .replace(' ', '') \
                                        .replace('\r', '')
                                    if line[-1:] == ':' or i % 2 != 0:
                                        content = item.text.replace('\t', '').replace('\n', '').replace(' ',
                                                                                                        '').replace(
                                            '\r', '')
                                        subContent = item.findNext().text.replace('\t', '').replace('\n', '').replace(
                                            ' ', '').replace('\r', '')
                                        # 有些登记机关后面没有":"，不能正确解析，导致插入企业信息不完整
                                        if line[-1:] != ':':
                                            lst.append(content + ':' + subContent)
                                        else:
                                            lst.append(content + subContent)

                                return lst


# 格式化网站信息
def parserWeb(data=''):
    if data != '':
        return parseDataById(data, 'resultTb2')


# 格式化公司信息和网站信息,返回dict
def parserCompanyAndWeb(data=''):
    if data != '':
        resultDict = {}
        # 公司信息
        companyList = parser(data);
        # 网站信息
        weblist = parseDataById(data, 'resultTb2')
        resultDict['company'] = companyList
        resultDict['web'] = weblist
        return resultDict


# 通过不同的id来提取信息
def parseDataById(data, id):
    soup = BeautifulSoup(data, 'html.parser')
    for table in soup.find_all('table'):
        if table.attrs.has_key('id'):
            if table.attrs['id'] == id:
                for sub_table in table.find_all('table'):
                    if sub_table.attrs.has_key('class'):
                        # print sub_table.attrs['class']
                        if sub_table.attrs['class'] == [u'list_boder']:
                            # print sub_table
                            lst = []
                            i = 0
                            for item in sub_table.find_all('td'):
                                i += 1
                                line = item.text.replace('\t', '') \
                                    .replace('\n', '') \
                                    .replace(' ', '') \
                                    .replace('\r', '')
                                if line[-1:] == [u':'] or i % 2 != 0 or line[-1:] == [u'：'] or line[-1:] == [u':']:
                                    content = item.text.replace('\t', '').replace('\n', '').replace(' ',
                                                                                                    '').replace(
                                        '\r', '').replace(':', ':')
                                    subContent = item.findNext().text.replace('\t', '').replace('\n', '').replace(
                                        ' ', '').replace('\r', '')
                                    lst.append(stringQ2B(content) + subContent)

                            return lst


if __name__ == '__main__':
    pass
    # datas  = parserFiles(rootdir='/home/bwh/tmp/gslz/nlz/')
    # print datas




    # lzlst=[u'4028e4c74c0d487d014c0d57327f4f9f', \
    #        u'2015100816060613', \
    #        u'20150928094605835',\
    #        u'4028e4c74c0d487d014c0d57327f4f9f',\
    #        u'4028e4c74c0d487d014c0d5730ea4e38']
    # #print parser(u'20151015115605697')
    # all=len(lzlst)
    # out=open('./query.txt','w')
    # for item in lzlst:
    #     print "第%s家/共%s家\n"%(lzlst.index(item)+1,all)
    #     out.write("第%s家/共%s家\n"%(lzlst.index(item)+1,all))
    #     for line in  parser(item):
    #         out.write(line.encode('utf8')+'\n')
    #         print line
    #     print "=============\n"
    #     out.write("=============\n")
    #     out.flush()
    #     import time
    #     time.sleep(5)
    # out.close()
