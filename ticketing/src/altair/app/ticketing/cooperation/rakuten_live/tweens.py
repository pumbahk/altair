from altair.app.ticketing.cooperation.rakuten_live.actions import store_r_live_request_param


def r_live_request_tween_factory(handler, registry):
    def r_live_request_tween(request):
        store_r_live_request_param(request, registry)
        response = handler(request)
        return response
    return r_live_request_tween
