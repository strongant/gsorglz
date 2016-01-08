# _*_ coding: UTF-8 _*_
import httplib


# 发送http请求GET方式
# host 访问的url
# port 端口号
# execute 需要请求的地址，比如/user/1
def httpGET(host, port, execute):
    try:
        httpClient = httplib.HTTPConnection(host, port, timeout=10)
        httpClient.request('GET', execute)
        # response是HTTPResponse对象
        response = httpClient.getresponse()
        return response
    except Exception, e:
        print e
    finally:
        if httpClient:
            httpClient.close()


# 通过POST方式发送http请求
# host 访问的url
# port 端口号
# execute 发送请求的地址,如/user
# params 需要发送的信息,如：{‘name’:'张三'}
def httpPOST(host, port, execute, params):
    httpClient = None
    try:
        headers = {'Content-type': 'application/x-www-form-urlencoded', 'Accept': 'text/plain'}
        httpClient = httplib.HTTPConnection(host, port, timeout=1000)
        httpClient.request('POST', execute, params, headers)
        response = httpClient.getresponse()
        return response.read()
    except Exception, e:
        print e
    finally:
        if httpClient:
            httpClient.close()
    return None


# 通过url信息读取网页内容
def read_url_info(url):
    content = None
    if url is not None:
        headers = {'Content-type': 'application/x-www-form-urlencoded', 'Accept': 'text/plain'}
        httpClient = httplib.HTTPConnection(url)
        httpClient.request('GET', headers=headers)
        response = httpClient.getresponse()
        content = response.read()
    return content
