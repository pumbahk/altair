# encoding: utf-8
import logging

# altair built-in library
from altair.sqlahelper import get_db_session
from altair.restful_framework import generics
from altair.restful_framework.fliters import FieldFilter, SearchFilter

# resale
from ..models import ResaleSegment, ResaleRequest
from .mixins import CSVExportModelMixin
from .serializers import ResaleSegmentSerializer, ResaleSegmentCreateSerializer, ResaleRequestSerializer
from .paginations import ResaleSegmentPageNumberPagination, ResaleRequestPageNumberPagination


logger = logging.getLogger(__name__)

class ResaleSegmentListAPIView(generics.ListAPIView):
    model = ResaleSegment
    serializer_class = ResaleSegmentSerializer
    pagination_class = ResaleSegmentPageNumberPagination
    filter_classes = (FieldFilter, )
    filter_fields = ['ResaleSegment.performance_id']

    # `get_dbsession`をoverrideしないと、masterのDBSessionを使う
    def get_dbsession(self):
        return get_db_session(self.request, 'slave')

class ResaleSegmentCreateAPIView(generics.CreateAPIView):
    model = ResaleSegment
    serializer_class = ResaleSegmentCreateSerializer

class ResaleSegmentRetrieveAPIView(generics.RetrieveAPIView):
    model = ResaleSegment
    serializer_class = ResaleSegmentSerializer

    # `get_dbsession`をoverrideしないと、masterのDBSessionを使う
    def get_dbsession(self):
        return get_db_session(self.request, 'slave')

class ResaleSegmentUpdateAPIView(generics.UpdateAPIView):
    model = ResaleSegment
    serializer_class = ResaleSegmentSerializer

class ResaleSegmentDestroyAPIView(generics.DestroyAPIView):
    model = ResaleSegment
    serializer_class = ResaleSegmentSerializer

class ResaleRequestListAPIView(generics.ListAPIView):
    model = ResaleRequest
    serializer_class = ResaleRequestSerializer
    pagination_class = ResaleRequestPageNumberPagination
    filter_classes = (FieldFilter, )
    filter_fields = ['ResaleRequest.resale_segment_id']

    # `get_dbsession`をoverrideしないと、masterのDBSessionを使う
    def get_dbsession(self):
        return get_db_session(self.request, 'slave')

class ResaleRequestCreateAPIView(generics.CreateAPIView):
    model = ResaleRequest
    serializer_class = ResaleRequestSerializer

class ResaleRequestRetrieveAPIView(generics.RetrieveAPIView):
    model = ResaleRequest
    serializer_class = ResaleRequestSerializer

    # `get_dbsession`をoverrideしないと、masterのDBSessionを使う
    def get_dbsession(self):
        return get_db_session(self.request, 'slave')

class ResaleRequestUpdateAPIView(generics.UpdateAPIView):
    model = ResaleRequest
    serializer_class = ResaleRequestSerializer

class ResaleRequestDestroyAPIView(generics.DestroyAPIView):
    model = ResaleRequest
    serializer_class = ResaleRequestSerializer

class ResaleRequestExportAPIView(CSVExportModelMixin, generics.GenericAPIView):
    model = ResaleRequest
    serializer_class = ResaleRequestSerializer
    filter_classes = (FieldFilter, SearchFilter)
    filter_fields = [
        'ResaleRequest.id',
        'ResaleRequest.resale_segment_id',
        'ResaleRequest.ordered_product_item_token_id',
        'ResaleRequest.bank_code',
        'ResaleRequest.bank_branch_code',
        'ResaleRequest.account_number',
        'ResaleRequest.account_holder_name',
        'ResaleRequest.total_amount'
    ]
    search_fields = [
        'ResaleRequest.id',
        'ResaleRequest.resale_segment_id',
        'ResaleRequest.ordered_product_item_token_id',
        'ResaleRequest.bank_code',
        'ResaleRequest.bank_branch_code',
        'ResaleRequest.account_number',
        'ResaleRequest.account_holder_name',
        'ResaleRequest.total_amount'
    ]

    # `get_dbsession`をoverrideしないと、masterのDBSessionを使う
    def get_dbsession(self):
        return get_db_session(self.request, 'slave')

    def get(self, request, *args, **kwargs):
        return self.export(request, *args, **kwargs)