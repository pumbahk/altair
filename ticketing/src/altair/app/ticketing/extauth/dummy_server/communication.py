import six
import hashlib
import json
from zope.interface import implementer
from pyramid.response import Response
from .interfaces import IRequestHandler
from .exceptions import BadParamError, BadRequestError, UnsupportedFlavor

@implementer(IRequestHandler)
class MembershipCheckAPIRequestHandler(object):
    def __init__(self, hash_key, client_registry, now_getter):
        self.hash_key = hash_key
        self.client_registry = client_registry
        self.now_getter = now_getter

    def handle_request(self, request):
        try:
            client_name = request.params['client_name']
            token = request.params['token']
            start_year = request.params['start_year']
            end_year = request.params['end_year']
        except KeyError as e:
            raise BadParamError(u'missing attribute %s' % e.message)
        openid_claimed_id = request.params.get('open_id')
        rakuten_easy_id = request.params.get('easy_id')
        if openid_claimed_id is None and rakuten_easy_id is None:
            raise BadParamError(u'either open_id or easy_id must be specified')
        if openid_claimed_id is not None and rakuten_easy_id is not None:
            raise BadParamError(u'open_id and easy_id cannot be specified at the same time')
        try:
            start_year = int(start_year)
        except (TypeError, ValueError):
            raise BadParamError(u'start_year must be a number')
        try:
            end_year = int(end_year)
        except (TypeError, ValueError):
            raise BadParamError(u'end_year must be a number')
        if start_year < 2000:
            raise BadParamError(u'start_year >= 2000')
        if end_year > 9999:
            raise BadParamError(u'end_year <= 9999')
        if end_year < start_year:
            raise BadParamError(u'end_year >= start_year')
        h = hashlib.sha224()
        if openid_claimed_id is not None:
            h.update(openid_claimed_id)
        else:
            h.update(rakuten_easy_id)
        h.update(client_name)
        h.update(self.hash_key)
        expected_token = h.hexdigest()
        if expected_token != token:
            raise BadParamError(u'invalid token value')
        try:
            client = self.client_registry[client_name]
        except:
            raise BadRequestError(u'client %s is not registered' % client_name)
        return dict(
            client=client,
            start_year=start_year,
            end_year=end_year,
            openid_claimed_id=openid_claimed_id,
            rakuten_easy_id=rakuten_easy_id
            )

    def format_datetime(self, value):
        return six.text_type(value.strftime(u'%Y-%m-%d %H:%M:%S')) if value is not None else None

    def build_response(self, request, flavor, successful, value):
        if flavor != u'json':
            raise UnsupportedFlavor(flavor)
        timestamp = self.now_getter(request)
        retval = {
            u'status': None,
            u'timestamp': self.format_datetime(timestamp),
            }
        if successful:
            retval[u'status'] = u'OK'
            retval[u'members'] = [
                {
                    u'fc_member_id': membership.membership_id,
                    u'fc_member_no': membership.user.member_no,
                    u'course_id': membership.kind.id,
                    u'course_name': membership.kind.name,
                    u'year': membership.valid_since.year,
                    u'admission_date': self.format_datetime(membership.created_at),
                    u'rakuten_relation_date': self.format_datetime(membership.user.related_at),
                    }
                for membership in value
                ]
        else:
            retval[u'status'] = u'NG'
            retval[u'message'] = value
        return Response(
            content_type='application/json',
            charset='utf-8',
            text=json.dumps(retval, ensure_ascii=False)
            )
