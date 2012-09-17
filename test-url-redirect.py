#!/usr/bin/python
# Author: Adam Portier <ajportier@gmail.com>

def getUrlFromIp(url,ip):
    '''Returns a string containing the URL, if there was a redirect (and where) targeted 
    at a specific IP'''
    import pycurl
    import cStringIO

    buffer = cStringIO.StringIO()
    url_parts = url.split('/')
    domain = url_parts.pop(0)
    page = '/'.join(url_parts)
    host_string = 'Host: ' + domain
    url_string = ip + '/' + page
    c = pycurl.Curl()
    c.setopt(c.URL, url_string)
    c.setopt(c.HTTPHEADER, [host_string]) 
    c.setopt(c.FOLLOWLOCATION, True)
    c.setopt(c.CONNECTTIMEOUT, 10)
    c.setopt(c.TIMEOUT, 15)
    c.setopt(c.WRITEFUNCTION, buffer.write)
    c.setopt(c.FAILONERROR, True)
    try:
        c.perform()
        end_url = c.getinfo(pycurl.EFFECTIVE_URL)
        redirect_count = c.getinfo(pycurl.REDIRECT_COUNT)
        if (redirect_count > 0):
            string = ' '.join((ip, url + '->' + end_url))
        else:
            string = ' '.join((ip, url))
    except pycurl.error, error:
        errorno, errstr = error
        string = ' '.join((ip, url, 'ERROR:', errstr))
    c.close()
    buffer.close()
    return string

def main():
    import sys

    servers = ['127.0.0.1']
    url = sys.argv[1]
    
    for ip in servers:
        string = getUrlFromIp(url,ip)
        print string

if __name__ == '__main__':
    main()
