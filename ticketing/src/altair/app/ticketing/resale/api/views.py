# encoding: utf-8
import json
import logging
from collections import OrderedDict

# 3rd party
from marshmallow import ValidationError
from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm.query import Query

# altair built-in library
from altair.sqlahelper import get_db_session

# resale
from ..models import ResaleSegment, ResaleRequest
from .serializers import ResaleSegmentSerializer, ResaleSegmentCreateSerializer, ResaleRequestSerializer, ResaleRequestCreateSerializer
from .pagination import Paginator, PageNotInInteger, EmptyPage
from .utils import remove_url_query_param, replace_url_query_param, ensure_positive_int

logger = logging.getLogger(__name__)

class ListAPIView(object):
    page_size = 25
    paginator_class =Paginator
    page_query_param = 'page'
    page_size_query_param = None
    max_page_size = None

    def get_paginated_query(self, request, query):
        self.request = request

        data = query.all() if isinstance(query, Query) else query
        page_size = self.get_page_size(self.request)
        page_number = self.request.params.get(self.page_query_param, 1)
        self.paginator = self.paginator_class(data, page_size)
        self.page = self.paginator.page(page_number)

        return list(self.page)

    def get_paginated_response(self, data):
        return Response(json=OrderedDict([
            ('count', self.page.paginator.count),
            ('page_size', self.page_size),
            ('next', self.next_link),
            ('previous', self.previous_link),
            ('page_range', self.page.paginator.page_range),
            ('data', data)
        ]))

    def get_page_size(self, request):
        if self.page_size_query_param:
            try:
                self.page_size = ensure_positive_int(
                    request.params.get(self.page_size_query_param, 25),
                    strict=True,
                    cutoff=self.max_page_size
                )
            except (KeyError, ValueError, TypeError):
                pass
        return self.page_size

    @property
    def next_link(self):
        if not self.page.has_next:
            return None
        url = self.request.current_route_url()
        page_number = self.page.next_page_number
        return replace_url_query_param(url, self.page_query_param, page_number)

    @property
    def previous_link(self):
        if not self.page.has_previous:
            return None
        url = self.request.current_route_url()
        page_number = self.page.previous_page_number
        if page_number == 1:
            return remove_url_query_param(url, self.page_query_param)
        return replace_url_query_param(url, self.page_query_param, page_number)


class ResaleSegmentListAPIView(ListAPIView):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.serializer = ResaleSegmentSerializer(many=True)
        self.session = get_db_session(self.request, 'slave')

    @view_config(route_name='api.segment.list', request_method='GET', renderer='json')
    def get(self):
        performance_id = self.request.params.get('performance_id', None)
        if not performance_id:
            return {'result': 'NG', 'emsgs': 'performance_id is required.'}

        resale_segments = self.session.query(ResaleSegment.id,
                                              ResaleSegment.start_at,
                                              ResaleSegment.end_at)\
                                       .filter_by(performance_id=performance_id)\
                                       .all()
        try:
            page = self.get_paginated_query(self.request, resale_segments)
            data = self.serializer.dump(page)
            return self.get_paginated_response(data)
        except (PageNotInInteger, EmptyPage) as err:
            return {'reuslt': 'NG', 'emsgs': str(err)}

class ResaleSegmentCreateAPIView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.serializer = ResaleSegmentCreateSerializer()

    @view_config(route_name='api.segment.create', request_method='POST', renderer='json')
    def post(self):

        try:
            data = self.serializer.load(self.request.POST)
        except ValidationError as err:
            return {'result': 'NG', 'emsgs': err.message}
        except Exception as err:
            return {'result': 'NG', 'emsgs': 'unknown error: {}'.format(str(err))}

        resales_segment = ResaleSegment()
        for key, val in data.items():
            setattr(resales_segment, key, val)
        resales_segment.save()
        logger.info('create the resale segment belong to performance: {0}'.format(self.request.POST['performance_id']))
        return {'results': 'OK', 'data': str(resales_segment.id)}

class ResaleSegmentAPIView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.serializer = ResaleSegmentSerializer()
        self.session = get_db_session(self.request, 'slave')

    @view_config(route_name='api.segment.detail', request_method='GET', renderer='json')
    def get(self):
        resale_segment_id = self.request.matchdict.get('resale_segment_id', None)

        try:
            resale_segment = self.session.query(ResaleSegment.id,
                                                ResaleSegment.start_at,
                                                ResaleSegment.end_at) \
                                         .filter_by(id=resale_segment_id) \
                                         .one()
        except (NoResultFound, MultipleResultsFound) as err:
            return {'result': 'NG', 'emsgs': str(err)}

        data = self.serializer.dump(resale_segment)
        return {'result': 'OK', 'data': json.dumps(data)}

    @view_config(route_name='api.segment.update', request_method='PUT', renderer='json')
    def put(self):
        resale_segment_id = self.request.matchdict.get('resale_segment_id', None)
        try:
            data = self.serializer.load(self.request.POST)
        except ValidationError as err:
            return {'result': 'NG', 'emsgs': err.message}
        except Exception as err:
            return {'result': 'NG', 'emsgs': 'unknown error: {}'.format(str(err))}

        resale_segment = ResaleSegment.get(resale_segment_id)
        for key, val in data.items():
            setattr(resale_segment, key, val)
        resale_segment.save()
        return {'result': 'OK', 'data': resale_segment_id}

    @view_config(route_name='api.segment.delete', request_method='DELETE', renderer='json')
    def delete(self):
        resale_segment_id = self.request.matchdict.get('resale_segment_id', None)
        resale_segment = ResaleSegment.get(resale_segment_id)
        resale_segment.delete()
        return {'result': 'OK', 'data': resale_segment_id}

class ResaleRequestListAPIView(ListAPIView):
    page_size_query_param = 'page_size'
    max_page_size = 100
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.serializer = ResaleRequestSerializer(many=True)
        self.session = get_db_session(self.request, 'slave')

    @view_config(route_name='api.request.list', request_method='GET', renderer='json')
    def get(self):
        resale_segment_id = self.request.matchdict.get('resale_segment_id', None)
        resale_requests = self.session.query(ResaleRequest).filter_by(resale_segment_id=resale_segment_id).all()

        try:
            page = self.get_paginated_query(self.request, resale_requests)
            data = self.serializer.dump(page)
            return self.get_paginated_response(data)
        except (PageNotInInteger, EmptyPage) as err:
            return {'reuslt': 'NG', 'emsgs': str(err)}

class ResaleRequestCreateAPIView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.serializer = ResaleRequestCreateSerializer()

    @view_config(route_name='api.request.create', request_method='POST', renderer='json')
    def post(self):
        try:
            data = self.serializer.load(self.request.POST)
        except ValidationError as err:
            return {'result': 'NG', 'emsgs': err.message}
        except Exception as err:
            return {'result': 'NG', 'emsgs': 'unknown error: {}'.format(str(err))}

        resale_request = ResaleRequest()
        for key, val in data.items():
            setattr(resale_request, key, val)
        resale_request.save()
        logger.info('create the resale segment belong to Resale Segment: {0}'.format(resale_request.resale_segment_id))
        return {'results': 'OK', 'data': str(resale_request.id)}

class ResaleRequestAPIView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.serializer = ResaleRequestSerializer()
        self.session = get_db_session(self.request, 'slave')

    @view_config(route_name='api.request.detail', request_method='GET', renderer='json')
    def get(self):
        resale_request_id = self.request.matchdict.get('resale_request_id', None)
        try:
            resale_request = self.session.query(ResaleRequest.id,
                                                ResaleRequest.ordered_product_item_token_id,
                                                ResaleRequest.bank_code,
                                                ResaleRequest.bank_branch_code,
                                                ResaleRequest.account_number,
                                                ResaleRequest.account_holder_name,
                                                ResaleRequest.total_amount) \
                                         .filter_by(id=resale_request_id) \
                                         .one()
        except (NoResultFound, MultipleResultsFound) as err:
            return {'result': 'NG', 'emsgs': str(err)}

        data = self.serializer.dump(resale_request)
        return {'result': 'OK', 'data': json.dumps(data)}


    @view_config(route_name='api.request.update', request_method='PUT', renderer='json')
    def put(self):
        resale_request_id = self.request.matchdict.get('resale_request_id', None)
        try:
            data = self.serializer.load(self.request.POST)
        except ValidationError as err:
            return {'result': 'NG', 'emsgs': err.message}
        except Exception as err:
            return {'result': 'NG', 'emsgs': 'unknown error: {}'.format(str(err))}

        resale_request = ResaleRequest.get(resale_request_id)
        for key, val in data.items():
            setattr(resale_request, key, val)
        resale_request.save()
        return {'result': 'OK', 'data': str(resale_request_id)}

    @view_config(route_name='api.request.delete', request_method='DELETE', renderer='json')
    def delete(self):
        resale_request_id = self.request.matchdict.get('resale_request_id', None)
        resale_request = ResaleRequest.get(resale_request_id)
        resale_request.delete()
        return {'result': 'OK', 'data': str(resale_request_id)}
