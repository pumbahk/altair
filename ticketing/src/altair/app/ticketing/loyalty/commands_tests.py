# -*- coding: utf-8 -*-

import unittest
from altair.app.ticketing.testing import _setup_db, _teardown_db
from altair.app.ticketing.core.models import (
            DBSession,
            Organization,
            OrganizationSetting,
)

from .commands import build_org_id_as_list

test_org = ["RT", "VK", "XX"]
test_point_type = [1, 0, None]

class CommandTest(unittest.TestCase):

    def setUp(self):
        self.session = _setup_db(modules=[
            "altair.app.ticketing.lots.models",
            "altair.app.ticketing.core.models",
            "altair.app.ticketing.orders.models",
        ])

        self.extra_orgs = ["VK"]

        for i, (code, point_type) in enumerate(zip(test_org, test_point_type)):
            print i, code
            orgSet = self._makeOrg(i+1, code, code, point_type)
            OrganizationSetting.add(orgSet)

        DBSession.flush()

    def tearDown(self):
        _teardown_db()

    def _makeOrg(self, org_id, code, short_name, point_type):
        OrgSet = OrganizationSetting()
        OrgSet.point_type = point_type
        OrgSet.organization = Organization(id=org_id, code=code, short_name=short_name)

        return OrgSet

    def test_build_org_id_as_list(self):
        organization = Organization.get(1)
        org_ids = build_org_id_as_list(organization)
        print org_ids
        self.assertEquals(len(org_ids), 2)
        self.assertEquals(1 in org_ids, True)
        self.assertEquals(2 in org_ids, True)
        self.assertEquals(3 in org_ids, False)