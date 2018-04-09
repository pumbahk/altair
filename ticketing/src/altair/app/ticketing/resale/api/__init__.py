# encoding: utf-8
from . import views


def includeme(config):
    # Resale Segment
    config.add_route('api.segment.list', '/segments')
    config.add_view(views.ResaleSegmentListAPIView.as_view(), route_name='api.segment.list')

    config.add_route('api.segment.create', '/segments/create')
    config.add_view(views.ResaleSegmentCreateAPIView.as_view(), route_name='api.segment.create')

    config.add_route('api.segment.detail', '/segments/{id}')
    config.add_view(views.ResaleSegmentRetrieveAPIView.as_view(), route_name='api.segment.detail')

    config.add_route('api.segment.update', '/segments/{id}/update')
    config.add_view(views.ResaleSegmentUpdateAPIView.as_view(), route_name='api.segment.update')

    config.add_route('api.segment.delete', '/segments/{id}/delete')
    config.add_view(views.ResaleSegmentDestroyAPIView.as_view(), route_name='api.segment.delete')

    # Resale Request
    config.add_route('api.request.list', '/requests')
    config.add_view(views.ResaleRequestListAPIView.as_view(), route_name='api.request.list')

    config.add_route('api.request.create', '/requests/create')
    config.add_view(views.ResaleRequestCreateAPIView.as_view(), route_name='api.request.create')

    config.add_route('api.request.export', '/requests/export')
    config.add_view(views.ResaleRequestExportAPIView.as_view(), route_name='api.request.export')

    config.add_route('api.request.detail', '/requests/{id}')
    config.add_view(views.ResaleRequestRetrieveAPIView.as_view(), route_name='api.request.detail')

    config.add_route('api.request.update', '/requests/{id}/update')
    config.add_view(views.ResaleRequestUpdateAPIView.as_view(), route_name='api.request.update')

    config.add_route('api.request.delete', '/requests/{id}/delete')
    config.add_view(views.ResaleRequestDestroyAPIView.as_view(), route_name='api.request.delete')

    config.scan('.')