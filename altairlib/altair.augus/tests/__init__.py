#-*- coding: utf-8 -*-
from unittest import TestCase
import os.path
from altair.augus.protocols import (
    VenueSyncRequest,
    VenueSyncResponse,
    PerformanceSyncRequest,
    TicketSyncRequest,
    DistributionSyncRequest,
    DistributionSyncResponse,
    PutbackRequest,
    PutbackResponse,
    PutbackFinish,
    AchievementRequest,
    AchievementResponse,
    ALL,
    )       

EXAMPLE_DIR = os.path.abspath(os.path.dirname(__file__)\
                            + '/../examples/protocol_data')
_ = lambda name: os.path.join(EXAMPLE_DIR, name)

PROTOCOL_EXAMPLE = {
    VenueSyncRequest: 'RT2500003KAI000000003_20130927164400.csv',
    VenueSyncResponse: None,
    PerformanceSyncRequest: 'RT2500003GME000000003_20130927165200.csv',
    TicketSyncRequest: 'RT2500003TKT000000003_20130927165400.csv',
    DistributionSyncRequest: 'RT2500003HAI000002968_201310011800_20130927165700.cs',
    DistributionSyncResponse: None,
    PutbackRequest: None,
    PutbackResponse: None,
    PutbackFinish: None,
    AchievementRequest: None,
    AchievementResponse: None,
    }

class ProtocolCountTest(TestCase):
    def test_it(self):
        self.assertEqual(len(ALL), len(PROTOCOL_EXAMPLE),
                         'The protocols count mismatch: {} {}'\
                         .format(len(ALL), len(PROTOCOL_EXAMPLE)))
