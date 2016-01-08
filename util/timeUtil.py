# _*_ coding: UTF-8 _*_
def calcInterval(time1,time2,tag):
    def calc(tag):
        return round(float((time1 - time2).seconds)/float(hs),len)
    len = 2
    ds = 3600*24
    hs = 3600
    ms = 60
    if tag=="h":
        interval = calc(hs)
    elif tag=="m":
        interval = calc(ds)
    elif tag=="d":
        ms
    return interval

