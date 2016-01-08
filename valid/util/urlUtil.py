# _*_ coding: UTF-8 _*_
import re


# 验证url的合法性
def validateUrl(url):
    # 定义验证url的规则
    regular = '((http|ftp|https):\/\/)?[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?'
    regex = re.compile(regular)
    result = regex.match(url)
    if result is not None:
        return True
    else:
        return False


# 将http://www.baidu.com/的域名格式返回baidu.com
def getShortDomain(domain):
    # 定义返回url的格式
    domainReg = 'www.(.*)/'
    result = re.findall(domainReg, domain)
    if result != [] and len(result) > 0:
        return result[0]
    return ''


# 返回www.baidu.com格式的域名
def getDomain(url):
    if 'http' in url:
        domainReg = '(www..*)/?'
        result = re.findall(domainReg, url)
        if result != [] and len(result) > 0:
            return result[0]
    elif re.findall('^www..*$', url) != [] and len(re.findall('^www..*$', url)) > 0:
        return url
    else:
        return None


def genShortUrl(url):
    if url != '':
        return url.replace("http://", '')
    else:
        return url


def isvalidUrl(url):
    # 验证无http网址
    regular = re.compile(u'(^(?:http|ftp)s?://)?(www\\.)?[\u4E00-\u9FA5\uF900-\uFA2D|\\w]+' \
                         u'\\.[\u4E00-\u9FA5\uF900-\uFA2D|\\w]+')
    if regular.match(url) is not None:
        return True
    else:
        return False
