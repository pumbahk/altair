# -*- coding:utf-8 -*-
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.views import BaseView
from altair.pyramid_dynamic_renderer import lbr_view_config
from pyramid.view import view_defaults


@view_defaults(decorator=with_bootstrap,
               renderer='altair.app.ticketing:templates/external_serial_code/settings/index.html',
               permission="event_editor")
class ExternalSerialCodeSettingView(BaseView):
    def __init__(self, context, request):
        super(ExternalSerialCodeSettingView, self).__init__(context, request)

    @lbr_view_config(route_name='external_serial_code_settings.index')
    def index(self):
        return {
        }
