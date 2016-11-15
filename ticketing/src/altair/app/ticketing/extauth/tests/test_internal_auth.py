# coding: utf-8
import unittest

from pyramid.testing import setUp, tearDown
from ..testing import _setup_db, _teardown_db

class NonguestAuthenticateTest(unittest.TestCase):
    def setUp(self):
        self.config = setUp(settings={})
        self.engine = _setup_db(
            self.config.registry,
            [
                'altair.app.ticketing.extauth.models',
                ])
        from altair.sqlahelper import get_global_db_session
        from datetime import date
        from ..models import Organization, Host, Member, MemberSet, MemberKind, Membership
        from ..api import digest_secret
        session = get_global_db_session(self.config.registry, 'extauth')
        self.organization = Organization(short_name=u'short_name')
        session.add(self.organization)
        session.flush()
        self.host = Host(host_name=u'host_name', organization_id=self.organization.id)
        self.organization.canonical_host_name = self.host.host_name
        self.member_set = MemberSet(
            name=u'member_set',
            display_name=u'member_set',
            use_password=True,
            organization=self.organization
            )
        self.member_kind = MemberKind(
            name=u'member_kind',
            display_name=u'member_kind',
            member_set=self.member_set
            )
        self.member = Member(
            auth_identifier=u'member',
            auth_secret=digest_secret(u'member', '01234567890123456789012345678901'),
            member_set=self.member_set,
            enabled=True,
            email=u'email@example.com',
            name=u'name',
            given_name=u'given_name',
            family_name=u'family_name',
            given_name_kana=u'given_name_kana',
            family_name_kana=u'family_name_kana',
            birthday=date(2000, 1, 1),
            gender=1,
            country=u'日本国',
            zip='0000000',
            prefecture=u'東京都',
            city=u'品川区',
            address_1=u'西五反田',
            address_2=u'五反田HSビル',
            tel_1=u'0000000000',
            tel_2=u'0000000001',
            memberships=[
                Membership(
                    member_kind=self.member_kind
                    )
                ]
            )
        session.add(self.member)
        session.commit()
        self.session = session

    def tearDown(self):
        _teardown_db(self.config.registry)
        tearDown()

    def test_ok(self):
        from datetime import date
        from ..internal_auth import nonguest_authenticate
        from altair.app.ticketing.testing import DummyRequest
        request = DummyRequest()
        self.assertEqual(
            nonguest_authenticate(
                request,
                dict(
                    member_set=self.member_set.name,
                    auth_identifier=self.member.auth_identifier,
                    auth_secret=u'member'
                    )
                ),
            (
                {
                    'member_id': 1,
                    'organization': u'short_name',
                    'host_name': u'host_name',
                    'auth_identifier': u'member',
                    'member_set': u'member_set',
                    'guest': False
                    },
                {
                    u'email_1': u'email@example.com',
                    u'nick_name': u'name',
                    u'first_name': u'given_name',
                    u'last_name': u'family_name',
                    u'first_name_kana': u'given_name_kana',
                    u'last_name_kana': u'family_name_kana',
                    u'birthday': date(2000, 1, 1),
                    u'gender': 1,
                    u'country': u'日本国',
                    u'zip': u'0000000',
                    u'prefecture': u'東京都',
                    u'city': u'品川区',
                    u'address_1': u'西五反田',
                    u'address_2': u'五反田HSビル',
                    u'tel_1': u'0000000000',
                    u'tel_2': u'0000000001',
                    }
                )
            )

    def test_disabled(self):
        from datetime import date
        from ..internal_auth import nonguest_authenticate
        from altair.app.ticketing.testing import DummyRequest
        request = DummyRequest()
        self.member.enabled = False
        self.session.commit()
        self.assertEqual(
            nonguest_authenticate(
                request,
                dict(
                    member_set=self.member_set.name,
                    auth_identifier=self.member.auth_identifier,
                    auth_secret=u'nonexistent_member'
                    )
                ),
            (None, None)
            )

    def test_nonexistent(self):
        from datetime import date
        from ..internal_auth import nonguest_authenticate
        from altair.app.ticketing.testing import DummyRequest
        request = DummyRequest()
        self.assertEqual(
            nonguest_authenticate(
                request,
                dict(
                    member_set=self.member_set.name,
                    auth_identifier=self.member.auth_identifier,
                    auth_secret=u'nonexistent_member'
                    )
                ),
            (None, None)
            )

class ValidateMemberTest(unittest.TestCase):
    def setUp(self):
        self.config = setUp(settings={})
        self.engine = _setup_db(
            self.config.registry,
            [
                'altair.app.ticketing.extauth.models',
                ])
        from altair.sqlahelper import get_global_db_session
        from datetime import date
        from ..models import Organization, Host, Member, MemberSet, MemberKind, Membership
        from ..api import digest_secret
        session = get_global_db_session(self.config.registry, 'extauth')
        self.organization = Organization(short_name=u'short_name')
        session.add(self.organization)
        session.flush()
        self.host = Host(host_name=u'host_name', organization_id=self.organization.id)
        self.organization.canonical_host_name = self.host.host_name
        self.member_set = MemberSet(
            name=u'member_set',
            display_name=u'member_set',
            use_password=True,
            organization=self.organization
            )
        self.member_kind = MemberKind(
            name=u'member_kind',
            display_name=u'member_kind',
            member_set=self.member_set
            )
        self.member = Member(
            auth_identifier=u'member',
            auth_secret=digest_secret(u'member', '01234567890123456789012345678901'),
            member_set=self.member_set,
            enabled=True,
            email=u'email@example.com',
            name=u'name',
            given_name=u'given_name',
            family_name=u'family_name',
            given_name_kana=u'given_name_kana',
            family_name_kana=u'family_name_kana',
            birthday=date(2000, 1, 1),
            gender=1,
            country=u'日本国',
            zip='0000000',
            prefecture=u'東京都',
            city=u'品川区',
            address_1=u'西五反田',
            address_2=u'五反田HSビル',
            tel_1=u'0000000000',
            tel_2=u'0000000001',
            memberships=[
                Membership(
                    member_kind=self.member_kind
                    )
                ]
            )
        session.add(self.member)
        session.commit()
        self.session = session

    def tearDown(self):
        _teardown_db(self.config.registry)
        tearDown()

    def test_ok(self):
        from datetime import date
        from ..internal_auth import validate_member
        from altair.app.ticketing.testing import DummyRequest
        request = DummyRequest()
        self.assertEqual(
            validate_member(
                request,
                dict(
                    member_id=self.member.id,
                    )
                ),
            (
                {
                    'member_id': 1,
                    'organization': u'short_name',
                    'host_name': u'host_name',
                    'auth_identifier': u'member',
                    'member_set': u'member_set',
                    'guest': False
                    },
                {
                    u'email_1': u'email@example.com',
                    u'nick_name': u'name',
                    u'first_name': u'given_name',
                    u'last_name': u'family_name',
                    u'first_name_kana': u'given_name_kana',
                    u'last_name_kana': u'family_name_kana',
                    u'birthday': date(2000, 1, 1),
                    u'gender': 1,
                    u'country': u'日本国',
                    u'zip': u'0000000',
                    u'prefecture': u'東京都',
                    u'city': u'品川区',
                    u'address_1': u'西五反田',
                    u'address_2': u'五反田HSビル',
                    u'tel_1': u'0000000000',
                    u'tel_2': u'0000000001',
                    }
                )
            )

    def test_disabled(self):
        from datetime import date
        from ..internal_auth import validate_member
        from altair.app.ticketing.testing import DummyRequest
        request = DummyRequest()
        self.member.enabled = False
        self.session.commit()
        self.assertEqual(
            validate_member(
                request,
                dict(
                    member_id=self.member.id
                    )
                ),
            (None, None)
            )
    def test_nonexistent(self):
        from datetime import date
        from ..internal_auth import validate_member
        from altair.app.ticketing.testing import DummyRequest
        request = DummyRequest()
        self.assertEqual(
            validate_member(
                request,
                dict(
                    member_id=0
                    )
                ),
            (None, None)
            )


