# encoding: utf-8

def includeme(config):
    # Resale Segment
    config.add_route('api.segment.list', '/segments')
    config.add_route('api.segment.create', '/segments/create')
    config.add_route('api.segment.detail', '/segments/{resale_segment_id}')
    config.add_route('api.segment.update', '/segments/{resale_segment_id}/update')
    config.add_route('api.segment.delete', '/segments/{resale_segment_id}/delete')

    # Resale Request
    config.add_route('api.request.list', '/segments/{resale_segment_id}/requests')
    config.add_route('api.request.create', '/segments/{resale_segment_id}/requests/create')
    config.add_route('api.request.detail', '/segments/{resale_segment_id}/requests/{resale_request_id}')
    config.add_route('api.request.update', '/segments/{resale_segment_id}/requests/{resale_request_id}/update')
    config.add_route('api.request.delete', '/segments/{resale_segment_id}/requests/{resale_request_id}/delete')

    config.scan('.')