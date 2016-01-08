# _*_ coding: UTF-8 _*_
import hashlib
import os
import xml.etree.cElementTree as ET

import xlrd
# 获取网址信息的文件名称：如,http://www.baidu.com/------获得的名称为www.baidu.com.html
from util.urlUtil import isvalidUrl



def getFileName(url):
    tmp = url
    if 'http://' in url:
        tmp = url[url.index('http://') + 7:]
        if '/' in tmp:
            tmp = tmp[:tmp.index('/')]
    elif 'https://' in url:
        tmp = url[url.index('https://') + 7:]
        if '/' in tmp:
            tmp = tmp[:tmp.index('/')]
    else:
        url = 'http://' + url
    filename = tmp + '.html'
    return filename


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


# 该方法用于根据指定的路径解析XML文件，并根据指定的TAG名称返回类型如:list[dict1,dict2,...]
def parseXMLFile(path, tagName):
    datas = []
    new = []
    if os.path.exists(path):
        tree = ET.ElementTree(file=path)
        for elem in tree.iter(tag=tagName):
            data = {}
            for subelem in elem:
                data[subelem.tag] = subelem.text
            datas.append(data)
    # 去除重复元素
    if len(datas)>0:
        func = lambda x, y: x if y in x else x + [y]
        result = reduce(func, [[], ] + datas)
        # 去除不规则网址
        for r in result:
            if isvalidUrl(r.get('url')):
                new.append(r)
    else:
        print "datas为空"
    return new


# 根据指定字符串计算hash值
def calcHash(str):
    return hashlib.md5(str).hexdigest()


def open_excel(file='file.xls'):
    try:
        data = xlrd.open_workbook(file)
        return data
    except Exception, e:
        print str(e)


# 根据索引获取Excel表格中的数据   参数:file：Excel文件路径     colnameindex：表头列名所在行的索引  ，by_index：表的索引
def excel_table_byindex(file=None, colnameindex=0, by_index=0):
    data = open_excel(file)
    table = data.sheets()[by_index]
    nrows = table.nrows  # 行数
    ncols = table.ncols  # 列数
    colnames = table.row_values(colnameindex)  # 某一行数据
    list = []
    for rownum in range(1, nrows):
        row = table.row_values(rownum)
        if row:
            app = {}
            for i in range(len(colnames)):
                app[colnames[i]] = row[i]
            list.append(app)
    return list


# 根据名称获取Excel表格中的数据   参数:file：Excel文件路径     colnameindex：表头列名所在行的所以  ，by_name：Sheet1名称
def excel_table_byname(file=None, colnameindex=0, by_name=u'Sheet1'):
    data = open_excel(file)
    table = data.sheet_by_name(by_name)
    nrows = table.nrows  # 行数
    colnames = table.row_values(colnameindex)  # 某一行数据
    list = []
    for rownum in range(1, nrows):
        row = table.row_values(rownum)
        if row:
            app = {}
            for i in range(len(colnames)):
                app[colnames[i]] = row[i]
            list.append(app)
    return list
