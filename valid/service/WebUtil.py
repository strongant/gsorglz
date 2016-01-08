# _*_coding: UTF-8_*_
import os
import re
import subprocess


def getGsLzUrl(file_path):
    # handle = subprocess.Popen("grep -Po '\"(.*entyId.*)\"' '%s' " % file_path, shell=True,
    #                           stdout=subprocess.PIPE)
    # content = ''.join(handle.communicate()[0].split()).replace('"','')  #去除空格.换行.双引号
    # return content
    context = open(file_path,'r')
    reg = '\href="(.*?entyId.*?)\"'
    result = re.findall(reg, context.read())
    if result != [] and len(result) > 0:
        return result[0].replace('amp;','')
    return ''

def getGsLzId(str):
    r =re.findall('.*entyId=(.*)',str)
    result = None
    if r !=[]:
        result = r[0]
    return  result




def buildKey(str):
    return mstr.replace(':','').replace('：','')

if __name__ == '__main__':
    filePath = '/home/bwh/tmp/gslz/nlz'
    fileNames=os.listdir(filePath)
    print filePath+'/%s'%fileNames[0]
    print "grep -Po '<td class=\"list_title_boeder\"[^>]*>(.*?)<\/td>'  '%s'  |grep -Po '(?<=\>)[^\<|\>]*(?=\<)' "%(filePath+'/%s'%fileNames[0])
    handle = subprocess.Popen("grep -Po '<td class=\"list_title_boeder\"[^>]*>(.*?)<\/td>'  '%s'  |grep -Po '(?<=\>)[^\<|\>]*(?=\<)' "%(filePath+'/%s'%fileNames[0]), shell=True,stdout=subprocess.PIPE)
    strs =  str(handle.communicate()[0]).split('\n')
    for mstr in strs:

        print buildKey(mstr)


    # for fileName in fileNames:
    #
    #     handle = subprocess.Popen(" grep -Po '<td class=\"list_title_boeder\"[^>]*>(.*?)<\/td>' %s |grep -Po '(?<=\>)[^\<|\>]*(?=\<)' "%fileName, shell=True,stdout=subprocess.PIPE)
    #     print ''.join(handle.communicate()[0].split())
    # handle = subprocess.Popen(" grep -Po '<td class=\"list_title_boeder\"[^>]*>(.*?)<\/td>' %s |grep -Po '(?<=\>)[^\<|\>]*(?=\<)' "%, shell=True,
    #                           stdout=subprocess.PIPE)
    #print ''.join(handle.communicate()[0].split())