#-*- coding: utf-8 -*-
from unittest import TestCase, skip
import os
from altair.augus.parsers import AugusParser
from altair.augus.errors import ProtocolNotFound

def _test_data(name):
    datadir = os.path.abspath(os.path.dirname(__file__)\
                              + '/../examples/protocol_data')
    return os.path.abspath(os.path.join(datadir, name))

class _AugusProtocolParseTest(object):
    PROTOCOL_FILE = ''
    
    def test_parse(self):
        parser = AugusParser()
        proto = parser.parse(self.PROTOCOL_FILE)

class VenueSyncRequestParseTest(TestCase, _AugusProtocolParseTest):
    PROTOCOL_FILE = _test_data('RT2500003KAI000000003_20130927164400.csv')


class _VenueSyncResponseParseTest(TestCase, _AugusProtocolParseTest):
    PROTOCOL_FILE = _test_data('')


class PerformanceSyncRequestParseTest(TestCase, _AugusProtocolParseTest):
    PROTOCOL_FILE = _test_data('RT2500003GME000000003_20130927165200.csv')


class TicketSyncRequestParseTest(TestCase, _AugusProtocolParseTest):
    PROTOCOL_FILE = _test_data('RT2500003TKT000000003_20130927165400.csv')



class DistributionSyncRequestParseTest(TestCase, _AugusProtocolParseTest):
    PROTOCOL_FILE = _test_data('RT2500003HAI000002968_201310011800_20130927165700.csv')


class _DistributionSyncResponseParseTest(TestCase, _AugusProtocolParseTest):
    PROTOCOL_FILE = _test_data('')


class _PutbackRequestParseTest(TestCase, _AugusProtocolParseTest):
    PROTOCOL_FILE = _test_data('')


class _PutbackResponseParseTest(TestCase, _AugusProtocolParseTest):
    PROTOCOL_FILE = _test_data('')


class _PutbackFinishParseTest(TestCase, _AugusProtocolParseTest):
    PROTOCOL_FILE = _test_data('')


class _AchievementRequestParseTest(TestCase, _AugusProtocolParseTest):
    PROTOCOL_FILE = _test_data('')


class _AchievementResponseParseTest(TestCase, _AugusProtocolParseTest):
    PROTOCOL_FILE = _test_data('')

class ProtocolNotFoundTest(TestCase):
    def test_protocol_not_found(self):
        with self.assertRaises(ProtocolNotFound):
            AugusParser.get_protocol('NOT_EXIST_PROTOCOL')
