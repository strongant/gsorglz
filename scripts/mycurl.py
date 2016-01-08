# -*- coding:utf-8 -*- 

__author__ = 'xhp'

import pycurl

from StringIO import StringIO

sglz='http://www.sgs.gov.cn/lz/licenseLink.do?method=licenceView&entyId='

def getLZ(lzid=''):
    #print lzid
    if lzid !='':
        #print lzid
        buffer = StringIO()
        c = pycurl.Curl()
        c.setopt(c.URL, sglz+lzid)
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        c.close()

        body = buffer.getvalue()
        # Body is a string in some encoding.
        # In Python 2, we can print it without knowing what the encoding is.
        #print(body)
        return body

if __name__=='__main__':
   print  getLZ('20131129184754956')