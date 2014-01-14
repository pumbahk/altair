#-*- coding: utf-8 -*-
from unittest import TestCase, skip
from mock import Mock, patch
from altair.augus.transporters import FTPTransporter

HOSTNAME = 'HOSTNAME'
USERNAME = 'USERNAME'
PASSWORD = 'PASSWORD'

class FTPTransporterTest(TestCase):
    def setUp(self):
        session = Mock()
        transporter = FTPTransporter(HOSTNAME, USERNAME, PASSWORD)
        transporter._conn = session        
        self.session = session        
        self.transporter = transporter

    @patch('ftplib.FTP')
    def test_create_session(self, FTP):
        FTP = Mock()
        self.transporter._create_session(HOSTNAME, USERNAME, PASSWORD)
        
    @patch('ftputil.FTPHost')
    def test_connect_disconnect(self, FTPHost):
        FTPHost = Mock(return_value=self.session)
        transporter = self.transporter
        
        transporter.disconnect()        
        self.assert_(not transporter.is_connect)
        
        transporter.connect()
        self.assert_(transporter.is_connect)

        transporter.disconnect()
        self.assert_(not transporter.is_connect)

        transporter.connect()
        self.assert_(transporter.is_connect)
        
        transporter.connect()
        self.assert_(transporter.is_connect)

        transporter.disconnect()
        self.assert_(not transporter.is_connect)

    def test_chdir(self):
        transporter = self.transporter
        args = ['/']
        kwds = {}
        transporter.chdir(*args, **kwds)

    def test_get(self): 
        transporter = self.transporter
        args = ['SRC', 'DST']
        kwds = {}
        transporter.get(*args, **kwds)
        
        args = ['SRC', 'DST']
        kwds = {'remove': True}
        transporter.get(*args, **kwds)
        
        args = ['SRC', 'DST']
        kwds = {'force': True}
        transporter.get(*args, **kwds)
        
        args = ['SRC', 'DST']
        kwds = {'remove': True, 'force': True}
        transporter.get(*args, **kwds)

    def test_put(self): 
        transporter = self.transporter
        args = ['SRC', 'DST']        
        kwds = {}
        transporter.put(*args, **kwds)
        
        kwds = {'parents': True}
        transporter.put(*args, **kwds)
        
        kwds = {'force': True}
        transporter.put(*args, **kwds)
        
        kwds = {'parents': True, 'force': True}
        transporter.put(*args, **kwds)

    def test_makedirs(self): 
        transporter = self.transporter
        args = ['SRC',]
        kwds = {}
        transporter.makedirs(*args, **kwds)

    def test_listdir(self): 
        transporter = self.transporter
        args = []
        kwds = {}
        transporter.listdir(*args, **kwds)

        args = ['SRC']
        kwds = {}
        transporter.listdir(*args, **kwds)
