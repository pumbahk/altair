#! /usr/bin/env python
#-*- coding: utf-8 -*-
import csv
import urllib
import httplib2
import optparse
from StringIO import StringIO
from pit import Pit
from BeautifulSoup import BeautifulSoup

def is_need_basic_auth(target):
    return target == 'stg2'

class Headers(dict):
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36'

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

    def __init__(self):
        self.headers = None
        self._http = httplib2.Http(
            '.cache',
            disable_ssl_certificate_validation=True)

    def basic_auth(self, username, password):
        self._http.add_credentials(username, password)

    def start(self):
        if self.headers is None:
            headers = Headers()
            headers.chrome_on_mac_mode()
            self.headers = headers
    
    def get(self, url, *args, **kwds):
        return self.request(url, 'GET', headers=self.headers, *args, **kwds)

    def post(self, url, *args, **kwds):
        return self.request(url, 'POST', headers=self.headers, *args, **kwds) 

    def request(self, *args, **kwds):
        res, contents = self._http.request(*args, **kwds)
        if res.status == 302: # http found
            url = res['location']
            return self.get(url)
        else:
            return res, contents

def _main():
    target = 'local'
    server_data = Pit.get('{0}_backend'.format(target),
                          {'require': {'username': '',
                                       'password': '',
                                       'url_login': '',
                                       'url_venue': '',
                                       }})
    bauth_data = Pit.get('{0}_basic'.format(target),
                         {'require': {'username': '',
                                      'password': '',
                                      }})

    url_login = server_data['url_login']
    url_venue = server_data['url_venue']    

    backend_login_data = {'login_id': server_data['username'].encode('utf8'),
                          'password': server_data['password'].encode('utf8'),
                          'submit': u'ログイン'.encode('utf8'),
                          }
    params = urllib.urlencode(backend_login_data)
    
    browser = Browser()
    browser.basic_auth(bauth_data['username'], bauth_data['password'])
    browser.start()
    res, content = browser.post(url_login, body=params)
    print content

def main():
    parser = optparse.OptionParser()
    opts, args = parser.parse_args()

    target = None
    try:
        target = args[0]
    except IndexError:
        target = 'stg2'

    server_data = Pit.get('{0}_backend'.format(target),
                          {'require': {'username': '',
                                       'password': '',
                                       'url_login': '',
                                       'url_venue': '',
                                       }})

    url_login = server_data['url_login']
    url_venue = server_data['url_venue']    

    http = httplib2.Http('.cache',
                         disable_ssl_certificate_validation=True)

    if is_need_basic_auth(target):
        bauth_data = Pit.get('{0}_basic'.format(target),
                             {'require': {'username': '',
                                          'password': '',
                                          }})
        http.add_credentials(bauth_data['username'], bauth_data['password'])

    # login
    #res, content = http.request(url_venue, 'GET')

    headers = Headers((
        ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'),
        ('Accept-Encoding', 'gzip,deflate,sdch'),
        ('Accept-Language', 'ja,en-US;q=0.8,en;q=0.6'),
        ('Authorization', 'Basic a2VudGE6bWF0c3Vp'),
        ('Cache-Control', 'max-age=0'),
        ('Coonection', 'keep-alive'),
        ('Content-type', 'application/x-www-form-urlencoded'),
        ('Origin', 'https://backend.stg2.rt.ticketstar.jp'),
        ('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36'),
        ('Referer', 'https://backend.stg2.rt.ticketstar.jp/login/'),
        ))
               
           
    backend_login_data = {'login_id': server_data['username'].encode('utf8'),
                          'password': server_data['password'].encode('utf8'),
                          'submit': u'ログイン'.encode('utf8'),
                          }
    params = urllib.urlencode(backend_login_data)
    res, content = http.request(url_login + '?', 'POST', headers=headers, body=params)
    headers.load(res)
    res, content = http.request(url_venue, 'GET', headers=headers)
    soup = BeautifulSoup(content)
    rows = soup.findAll('tr')
    rows = filter(lambda tr: tr.has_key('id') and tr['id'].startswith('venue-'), rows)
    venue_ids = []
    for row in rows:
        data = row.findAll('td')
        atag = data[5].find('a')
        venue_id = row['id'].replace('venue-', '')
        if not atag:
            venue_ids.append(venue_id)

    
    for venue_id in venue_ids:
        print venue_id,
        res, content = http.request(
            'https://backend.stg2.rt.ticketstar.jp/cooperation/download/{0}?id=&cooperation_type=1'.format(venue_id),
            'GET', headers=headers)
        if res.status != 200:
            print res.status, '--------------->', 'NG'
        else:
            print
        continue

        old = StringIO(content)
        old.seek(0)        
        new = StringIO()
        
        reader = csv.reader(old)
        writer = csv.writer(new, delimiter=',')
        
        writer.writerow(reader.next()) # header
        
        for row in reader:
            name = row[1]
            seat_no = row[2]
            group_l0_id = row[4]
            row_l0_id = row[5]
            data = row[:6] + [venue_id, 1, 1, group_l0_id, row_l0_id, name]
            writer.writerow(data)
        new.seek(0)

        res, content = http.request(
            'https://backend.stg2.rt.ticketstar.jp/cooperation/download/{0}?id=&cooperation_type=1'.format(venue_id),
            'POST', headers=headers, body=new.read())
        import ipdb; ipdb.set_trace()
        pass
        
            
if __name__ == '__main__':
    main()

