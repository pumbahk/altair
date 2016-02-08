import unittest
import mock

class MemberDataParserTests(unittest.TestCase):
    def test_tkt1030(self):
        from ..import_export import MemberDataParser
        from ...models import MemberSet, MemberKind
        slave_session = mock.Mock()
        def _(arg):
            retval = mock.Mock()
            if arg is MemberSet:
                retval.filter_by.return_value.one.return_value.name = u'member_set'
            elif arg is MemberKind:
                retval.filter_by.return_value.one.return_value.name = u'member_kind'
            return retval
        slave_session.query = _
        target = MemberDataParser(
            slave_session=slave_session,
            organization_id=1
            )
        reader = mock.Mock()
        raw_record = {
            u'auth_identifier': 10000001,
            u'auth_secret': 10000001,
            u'member_set': u'member_set',
            u'member_kind': u'member_kind',
            u'membership_identifier': 20000001,
            }
        errors, result = target.convert_to_record(reader, raw_record)
        self.assertEqual(len(errors), 0)
        self.assertEqual(result['auth_identifier'], u'10000001')
        self.assertEqual(result['auth_secret'], u'10000001')
        self.assertEqual(result['membership_identifier'], u'20000001')
