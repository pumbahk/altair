#! /usr/bin/env python
#-*- coding: utf-8 -*-
import urllib
import httplib2
from StringIO import StringIO
from pit import Pit

class Headers(dict):
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.36 (KHTML, like Gecko) '\
                 'Chrome/31.0.1650.63 Safari/537.36'

    def __init__(self, *args, **kwds):
        super(Headers, self).__init__(*args, **kwds)
        self._cookies = {}
        
    def load(self, res):
        for header in res.keys():
            if header.lower() == 'set-cookie':
                key, value = res[header].split('=', 1)
                self._cookies[key] = value
        if self._cookies:
            self['Cookie'] = ';'.join([' {0}={1}'.format(key, value) for key, value in self._cookies.items()]).strip()

    def chrome_on_mac_mode(self):
        for key, value in (('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'),
                           ('Accept-Encoding', 'gzip,deflate,sdch'),
                           ('Accept-Language', 'ja,en-US;q=0.8,en;q=0.6'),
                           ('Cache-Control', 'max-age=0'),
                           ('User-Agent', self.user_agent),
                           ):
            self[key] = value


class Browser(object):
    def __init__(self, cache='.cache'):
        self._http = httplib2.Http(cache, disable_ssl_certificate_validation=True)
        self._headers = None
        self.header_init()

    def header_init(self):
        self._headers = Headers((
            ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'),
            ('Accept-Encoding', 'gzip,deflate,sdch'),
            ('Accept-Language', 'ja,en-US;q=0.8,en;q=0.6'),
            ('Authorization', 'Basic a2VudGE6bWF0c3Vp'),
            ('Cache-Control', 'max-age=0'),
            ('Coonection', 'keep-alive'),
            ('Content-type', 'application/x-www-form-urlencoded'),
            ('Origin', 'https://backend.stg2.rt.ticketstar.jp'),
            ('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) '\
             'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36'),
            ('Referer', 'https://backend.stg2.rt.ticketstar.jp/login/'),
        ))
    
    def basic_auth(self, username, password):
        self._http.add_credentials(username, password)

    def request(self, url, method, headers=None, **kwds):
        print url, kwds
        if not headers:
            headers = self._headers
        res, content = self._http.request(url, method, headers=headers, **kwds)
        headers.load(res)
        if res.status == 302: # http found
            url = res['location']
            res, content =  self.get(url, **kwds)
        return res, content

    def get(self, url, *args, **kwds):
        return self.request(url, 'GET', *args, **kwds)

    def post(self, url, *args, **kwds):
        return self.request(url, 'POST', *args, **kwds)


class AltairBackendBrowser(Browser):
    def set_host(self, host):
        if not host.endswith('/'):
            host += '/'
        self.host = host
        if self.host in 'https://backend.stg2.rt.ticketstar.jp/':
            settings = Pit.get('stg2', {'require': {'basic_username': '',
                                                    'basic_password': '',
                                                    }})
            username = settings['basic_username']
            password = settings['basic_password']
            self.basic_auth(username, password)
        
    def login(self, account):
        url = self.host + 'login/'
        settings = Pit.get(account, {'require': {'username': '',
                                                 'password': '',
                                                 }})
        username = settings['username']
        password = settings['password']
        backend_login_data = {'login_id': username.encode('utf8'),
                              'password': password.encode('utf8'),
                              'submit': u'ログイン'.encode('utf8'),
                              }
        params = urllib.urlencode(backend_login_data)
        res, content = self.post(url, body=params)
        return res, content

    def download_augus_venue(self, venue_id, augus_venue_version=None):
        url = self.host + 'cooperation/augus/venues/{}/download'.format(venue_id)
        res, content = self.get(url)
        fp = StringIO(content)
        fp.seek(0)
        return fp

        
def main():
    browser = AltairBackendBrowser()
    browser.set_host('https://backend.stg2.rt.ticketstar.jp')
    res, content = browser.login('RT')
    fp = browser.download_augus_venue(868)
    print fp.read()

if __name__ == '__main__':
    main()
