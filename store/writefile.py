# _*_ coding: UTF-8 _*_
import csv

import os


# 将解析后的csv文件进行保存到项目根目录下的temp文件夹下
def writeCSV(filePath, fileHashName, fileData):
    result = None
    taskFileName = '%s.csv' % fileHashName
    # 将文件写入指定目录下
    csvpath = os.path.join(filePath, taskFileName)
    # 判断目录下是否已经存在该文件
    if os.path.exists(csvpath):
        print '文件已经存在'
        result = None
    else:
        try:
            csvfile = file(csvpath, 'wb')
            writer = csv.writer(csvfile)
            data = fileData.split('\n')
            for line in data:
                templist = [line]
                writer.writerow(templist)
            csvfile.close()
            result = True
        except Exception, e:
            result = False
            print e
    return result


def writeXML(filePath,fileData):
    #taskFileName = filePath
    # 将文件写入指定目录下
    #path = os.path.join(filePath, taskFileName)
    # 判断目录下是否已经存在该文件
    if os.path.exists(filePath):
        print '文件已经存在'
        result = None
    else:
        try:
            file = open(filePath, 'w')
            file.write(fileData)
            file.flush()
            file.close()
            result = True
        except Exception, e:
            result = False
            print e
    return result
