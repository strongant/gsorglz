/*
 #  #
 */

var charset, cookies, headers, page, page_url, savePath, read_args, request_timeout, system, timeout, init_page, downloadHtml;
system = require("system");
page = require('webpage').create();
fs = require('fs');
page_url = null;
charset = 'utf-8';
request_timeout = 5000;
timeout = 30 * 1000;
cookies = [];
headers = {};


read_args = function () {
    var e;
    page_url = system.args[1];
    savePath = system.args[2];
    charset = system.args[3];
    request_timeout = parseInt(system.args[4]);
    timeout = parseInt(system.args[5]);
    try {
        cookies = JSON.parse(system.args[6]);
    } catch (_error) {
        e = _error;
        cookies = [];
    }
    try {
        return headers = JSON.parse(system.args[7]);
    } catch (_error) {
        e = _error;
        return headers = {};
    }
};

init_page = function () {
    var cookie, expires, _i, _len;
    page.settings.resourceTimeout = request_timeout;
    expires = (new Date()).getTime() + (1000 * 60 * 60);
    for (_i = 0, _len = cookies.length; _i < _len; _i++) {
        cookie = cookies[_i];
        cookie['httponly'] = page_url.indexOf('https://') === 0;
        cookie['expires'] = expires;
        phantom.addCookie(cookie);
    }
    page.settings.userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.29 Safari/537.36';
    return page.customHeaders = headers;
};
downloadHtml = function () {
    setTimeout(function () {
        var html = page.content;
        fs.write(savePath, html, 'w');
        page.close();
        phantom.exit();
    }, timeout);
};
read_args();
init_page();


page.open(page_url, function (status) {
        if (status === 'success') {
            downloadHtml()
        } else {
            page.close();
            phantom.exit();
        }
    }
);
