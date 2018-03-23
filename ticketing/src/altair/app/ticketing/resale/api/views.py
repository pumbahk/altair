# encoding: utf-8
import logging

# altair built-in library
from altair.sqlahelper import get_db_session
from altair.restful_framework import generics
from altair.restful_framework.fliters import FieldFilter

# resale
from ..models import ResaleSegment, ResaleRequest
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
