# -*- coding: utf-8 -*-

import re
import hashlib
from struct import pack, unpack

C32 = "0123456789ABCDEFGHIJKLMNOPQRSTUV"
C42 = "$%*+/.0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

C32r = dict([(C32[i], i) for i in range(len(C32))])
C42r = dict([(C42[i], i) for i in range(len(C42))])

tag2int = {
    "serial": 1,
    "order": 10,
    "performance": 11,
    "date": 12,
    "type": 13,
    "seat": 14,
    }
int2tag = dict([(tag2int[t], t) for t in tag2int])

class qr:
    def enc32(self, i):
        """encode 0-31 integer"""
        if i < 32:
            return C32[i]
        raise BaseException("too large number %d" % i)
    
    def dec32(self, c):
        """decode 0-31 integer"""
        return C32r[c]
    
    def enc32m(self, i, size=0):
        """encode integer to variable-length string"""
        buf = [ ]
        while 1:
            buf.insert(0, C32[(i%16) + (16 if len(buf)==0 else 0)])
            if i < 16:
                break;
            i = i/16
        if 0 < size:
            while len(buf) < size:
                buf.insert(0, C32[0])
            if size < len(buf):
                raise BaseException("too large number: %d" % i)
        return "".join(buf)
    
    def __shift32m(self, list):
        """decode integer from head of string"""
        i = 0
        while 1:
            a = C32r[list.pop(0)]
            if a < 16:
                i = i*16 + a
            else:
                i = i*16 + a - 16
                break
        return i
    
    def enc42(self, s):
        """encode string"""
        return "".join([self.__enc42c(c) for c in list(s)])
    
    def __enc42c(self, c):
        """encode 1 char (some ASCII or Unicode char compatible to EUC-JP)"""
        if re.compile('[0-9A-Z: -]').match(c):
            return c
        
        bin = unpack('!H', c.encode("eucjp"))[0]
        if bin/256 < 160 or bin%256 < 160:
            raise BaseException("Out of range: %s" % c)
        mid = (bin/256-160)*96 + (bin%256-160)
        return "".join([C42[i] for i in (mid/42/42, (mid/42)%42, mid%42)])
    
    def dec42(self, s):
        """decode string"""
        buf = [ ]
        s = list(s)
        while 0 < len(s):
            if re.compile('[0-9A-Z: -]').match(s[0]):
                buf.append(s.pop(0))
            else:
                i = (C42r[s[0]]*42+C42r[s[1]])*42+C42r[s[2]]
                c = pack('!H', (i/96+160)*256 + i%96+160)
                buf.append(c.decode("eucjp"))
                s = s[3:]
        return "".join(buf)
    
    def encdate(self, ymd):
        """encode date(YYYYMMDD string)"""
        return "".join((self.enc32m(int(ymd[0:4])-2000, 2), self.enc32(int(ymd[4:6])), self.enc32(int(ymd[6:8]))))
    
    def decdate(self, s):
        """decode date"""
        return "%04u%02u%02u" % (2000+self.__shift32m(list(s[0:2])), self.dec32(s[2]), self.dec32(s[3]))
    
    def __pair(self, tag, content):
        buf = [ ]
        buf.append(self.enc32m(tag2int[tag]))
        buf.append(self.enc32m(len(content)))
        buf.append(content)
        return "".join(buf)
    
    def make(self, data):
        """make QR ticket data"""
        buf = [ ]
        buf.append(self.__pair("serial", data["serial"]))
        buf.append(self.__pair("performance", data["performance"]))
        buf.append(self.__pair("order", data["order"]))
        buf.append(self.__pair("date", self.encdate(data["date"])))
        buf.append(self.__pair("type", self.enc32m(data["type"])))
        buf.append(self.__pair("seat", self.enc42(data["seat"])))
        return "".join(buf)
    
    def parse(self, qr):
        """parse QR ticket data"""
        d = dict()
        
        s = list(qr)
        while 2 <= len(s):
            tag = int2tag[self.__shift32m(s)]
            size = self.__shift32m(s)
            d[tag] = "".join(s[0:size]).encode("ascii")
            s = s[size:]
        
        d["date"] = self.decdate(d["date"])
        d["type"] = self.__shift32m(list(d["type"]))
        d["seat"] = self.dec42(list(d["seat"]))
        
        return d
    
    def sign(self, body):
        h = hashlib.sha1()
        h.update("".join((body, self.key)))
        sig8 = unpack('BBBBB', h.digest()[0:5]) # first 40bit
        sig5 = [ ]
        sig5.append((sig8[0]&0xf8) >> 3)
        sig5.append((sig8[0]&0x07) << 2 | (sig8[1]&0xc0) >> 6)
        sig5.append((sig8[1]&0x3e) >> 1)
        sig5.append((sig8[1]&0x01) << 4 | (sig8[2]&0xf0) >> 4)
        sig5.append((sig8[2]&0x0f) << 1 | (sig8[3]&0x80) >> 7)
        sig5.append((sig8[3]&0x7c) >> 2)
        sig5.append((sig8[3]&0x03) << 3 | (sig8[4]&0xe0) >> 5)
        sig5.append((sig8[4]&0x1f))
        return "".join(([self.enc32(c) for c in sig5])) + body
    
    def validate(self, signbody):
        return self.sign(signbody[8:]) == signbody
