# encoding: utf-8
import logging
import re

# altair built-in library
from altair.sqlahelper import get_db_session
from altair.restful_framework import generics
from altair.restful_framework.fliters import FieldFilter, SearchFilter

# resale
from ..models import ResaleSegment, ResaleRequest
from .mixins import CSVExportModelMixin, AlternativePermissionMixin
from .serializers import ResaleSegmentSerializer, ResaleSegmentCreateSerializer, ResaleRequestSerializer
from .paginations import ResaleSegmentPageNumberPagination, ResaleRequestPageNumberPagination
from .permissions import ResaleAltairPermission, ResaleAPIKeyPermission

# orders
from altair.app.ticketing.orders.models import Order, OrderedProduct, OrderedProductItem, OrderedProductItemToken

logger = logging.getLogger(__name__)


class ResaleSegmentListAPIView(AlternativePermissionMixin, generics.ListAPIView):
    model = ResaleSegment
    serializer_class = ResaleSegmentSerializer
    pagination_class = ResaleSegmentPageNumberPagination
    alternative_permission_classes = [ResaleAltairPermission, ResaleAPIKeyPermission]
    filter_classes = (FieldFilter, )
    filter_fields = ['ResaleSegment.performance_id']

    # `get_dbsession`をoverrideしないと、masterのDBSessionを使う
    def get_dbsession(self):
        return get_db_session(self.request, 'slave')


class ResaleSegmentCreateAPIView(generics.CreateAPIView):
    model = ResaleSegment
    serializer_class = ResaleSegmentCreateSerializer
    permission_classes = [ResaleAltairPermission]


class ResaleSegmentRetrieveAPIView(AlternativePermissionMixin, generics.RetrieveAPIView):
    model = ResaleSegment
    serializer_class = ResaleSegmentSerializer
    alternative_permission_classes = [ResaleAltairPermission, ResaleAPIKeyPermission]

    # `get_dbsession`をoverrideしないと、masterのDBSessionを使う
    def get_dbsession(self):
        return get_db_session(self.request, 'slave')


class ResaleSegmentUpdateAPIView(generics.UpdateAPIView):
    model = ResaleSegment
    serializer_class = ResaleSegmentSerializer
    permission_classes = [ResaleAltairPermission]


class ResaleSegmentDestroyAPIView(generics.DestroyAPIView):
    model = ResaleSegment
    serializer_class = ResaleSegmentSerializer
    permission_classes = [ResaleAltairPermission]


class ResaleRequestListAPIView(AlternativePermissionMixin, generics.ListAPIView):
    model = ResaleRequest
    serializer_class = ResaleRequestSerializer
    pagination_class = ResaleRequestPageNumberPagination
    alternative_permission_classes = [ResaleAltairPermission, ResaleAPIKeyPermission]
    filter_classes = (FieldFilter, SearchFilter)
    filter_fields = [
        'ResaleRequest.id',
        'ResaleRequest.resale_segment_id',
        'ResaleRequest.ordered_product_item_token_id',
        'ResaleRequest.bank_code',
        'ResaleRequest.bank_branch_code',
        'ResaleRequest.account_type',
        'ResaleRequest.account_number',
        'ResaleRequest.account_holder_name',
        'ResaleRequest.total_amount',
        'ResaleRequest.sold_at',
        'ResaleRequest.status',
        'ResaleRequest.sent_status',
        'ResaleRequest.sent_at'
    ]
    search_fields = [
        'ResaleRequest.id',
        'ResaleRequest.resale_segment_id',
        'ResaleRequest.ordered_product_item_token_id',
        'ResaleRequest.bank_code',
        'ResaleRequest.bank_branch_code',
        'ResaleRequest.account_type',
        'ResaleRequest.account_number',
        'ResaleRequest.account_holder_name',
        'ResaleRequest.total_amount',
        'ResaleRequest.sold_at',
        'ResaleRequest.status',
        'ResaleRequest.sent_status',
        'ResaleRequest.sent_at'
    ]

    # `get_dbsession`をoverrideしないと、masterのDBSessionを使う
    def get_dbsession(self):
        return get_db_session(self.request, 'slave')


class ResaleRequestCreateAPIView(AlternativePermissionMixin, generics.CreateAPIView):
    model = ResaleRequest
    serializer_class = ResaleRequestSerializer
    alternative_permission_classes = [ResaleAltairPermission, ResaleAPIKeyPermission]


class ResaleRequestRetrieveAPIView(AlternativePermissionMixin, generics.RetrieveAPIView):
    model = ResaleRequest
    serializer_class = ResaleRequestSerializer
    alternative_permission_classes = [ResaleAltairPermission, ResaleAPIKeyPermission]

    # `get_dbsession`をoverrideしないと、masterのDBSessionを使う
    def get_dbsession(self):
        return get_db_session(self.request, 'slave')


class ResaleRequestUpdateAPIView(generics.UpdateAPIView):
    model = ResaleRequest
    serializer_class = ResaleRequestSerializer
    alternative_permission_classes = [ResaleAltairPermission, ResaleAPIKeyPermission]


class ResaleRequestDestroyAPIView(generics.DestroyAPIView):
    model = ResaleRequest
    serializer_class = ResaleRequestSerializer
    alternative_permission_classes = [ResaleAltairPermission, ResaleAPIKeyPermission]


class ResaleRequestExportAPIView(CSVExportModelMixin, generics.GenericAPIView):
    model = ResaleRequest
    serializer_class = ResaleRequestSerializer
    permission_classes = [ResaleAltairPermission]
    filter_classes = (FieldFilter, SearchFilter)
    filter_fields = [
        'ResaleRequest.id',
        'ResaleRequest.resale_segment_id',
        'ResaleRequest.ordered_product_item_token_id',
        'ResaleRequest.bank_code',
        'ResaleRequest.bank_branch_code',
        'ResaleRequest.account_type',
        'ResaleRequest.account_number',
        'ResaleRequest.account_holder_name',
        'ResaleRequest.total_amount',
        'ResaleRequest.sold_at',
        'ResaleRequest.status',
        'ResaleRequest.sent_status',
        'ResaleRequest.sent_at'
    ]
    search_fields = [
        'ResaleRequest.id',
        'ResaleRequest.resale_segment_id',
        'ResaleRequest.ordered_product_item_token_id',
        'ResaleRequest.bank_code',
        'ResaleRequest.bank_branch_code',
        'ResaleRequest.account_type',
        'ResaleRequest.account_number',
        'ResaleRequest.account_holder_name',
        'ResaleRequest.total_amount',
        'ResaleRequest.sold_at',
        'ResaleRequest.status',
        'ResaleRequest.sent_status',
        'ResaleRequest.sent_at'
    ]

    # `get_dbsession`をoverrideしないと、masterのDBSessionを使う
    def get_dbsession(self):
        return get_db_session(self.request, 'slave')

    def get(self, request, *args, **kwargs):
        return self.export(request, *args, **kwargs)

    def filter_query(self, query):
        order_no = self.request.params.get('order_no', None)
        if order_no:
            order_no_list = re.split(r'[ \t,]', order_no)
            query = query.join(OrderedProductItemToken,
                               ResaleRequest.ordered_product_item_token_id == OrderedProductItemToken.id) \
                         .join(OrderedProductItem,
                               OrderedProductItemToken.ordered_product_item_id == OrderedProductItem.id) \
                         .join(OrderedProduct,
                               OrderedProductItem.ordered_product_id == OrderedProduct.id) \
                         .join(Order,
                               OrderedProduct.order_id == Order.id) \
                         .filter(Order.order_no.in_(order_no_list))
        
        return super(ResaleRequestExportAPIView, self).filter_query(query)
