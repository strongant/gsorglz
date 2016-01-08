# _*_coding: UTF-8_*_
# 通过外部定义的参数返回网站首页代码
import gc
import json
import os
import subprocess
import sys
import time


def downloadByPhantom(phantomjs_path, scarping_js_path,
                      url, charset,
                      request_timeout, timeout,
                      cookies, headers):
    args = [phantomjs_path,
            '--ssl-protocol=any', scarping_js_path,
            url, charset, request_timeout,
            timeout, json.dumps(cookies),
            json.dumps(headers)]
    env = getattr(os, 'environb', os.environ)
    formated_env = {}
    for key, value in env.iteritems():
        if isinstance(key, unicode):
            try:
                key = key.encode(charset)
            except Exception:
                key = key.encode('utf-8', errors='ignore')
        if isinstance(value, unicode):
            try:
                value = value.encode(charset)
            except Exception:
                value = value.encode('utf-8', errors='ignore')
        formated_env[key] = value
    gc.collect()
    try:
        reload(sys)
        sys.setdefaultencoding('utf-8')
        process = subprocess.Popen(args, close_fds=True, stdout=subprocess.PIPE, env=formated_env)
        # process.wait()
        out = process.stdout.readlines()
        if process.stdin:
            process.stdin.close()
        if process.stdout:
            process.stdout.close()
        if process.stderr:
            process.stderr.close()
        try:
            process.kill()
        except OSError:
            pass
        return out
    except Exception, e:
        print e


def downloadByPath(url, path):
    f = None
    filename = path
    # 将打不开的url进行记录
    logFile = open('../logs/error.log', 'a')
    try:

        print 'path:', path
        data = downloadByPhantom('/usr/bin/phantomjs', '../phantomjs/fetch.js', url, 'utf-8',
                                 str(1000 * 5),
                                 str(1000 * 10), [],
                                 {})
        print 'first data:', data
        if data is None:
            filename = None
        else:
            newDict = parsePageContent(data)

            if newDict.get('status') == 'success':
                f = open(os.path.join(path), 'w')
                f.write(str(newDict.get('content')))
            else:
                time.sleep(3)
                # 重试一次
                print 'retry'
                filename = haveTry(path, url)
    except Exception, e:
        logFile.write(url + '\n')
        filename = None
        print e
    finally:
        if f:
            f.flush()
        if f:
            f.close()
        if f:
            logFile.close()
    return filename


def parsePageContent(data):
    newDict = {}
    for json in data:
        if json.find('{"status":') != -1:
            tempDict = eval(json)
            newDict['status'] = tempDict.get('status')
        elif json.find('{"content":') != -1:
            tempDict = eval(json)
            newDict['content'] = tempDict.get('content')
    return newDict


def haveTry(filename, url):
    tempData = downloadByPhantom('/usr/bin/phantomjs', '../phantomjs/fetch.js', url, 'utf-8',
                                 str(1000 * 5),
                                 str(1000 * 60), [],
                                 {})
    print 'tempData:', tempData
    if tempData is None:
        filename = None
    else:
        try:
            newDict = parsePageContent(tempData)
            if newDict.get('status') == 'success':
                f = open(os.path.join(filename), 'w')
                f.write(newDict.get('content'))
            else:
                filename = None
        except Exception, e:
            print e
    return filename
