# -*- coding:utf-8 -*-
import webhelpers.paginate as paginate
from altair.app.ticketing.core.utils import PageURL_WebOb_Ex
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.views import BaseView
from altair.pyramid_dynamic_renderer import lbr_view_config
from pyramid.view import view_defaults
from pyramid.httpexceptions import HTTPNotFound


@view_defaults(decorator=with_bootstrap,
               permission="event_editor")
class ExternalSerialCodeSettingView(BaseView):
    def __init__(self, context, request):
        super(ExternalSerialCodeSettingView, self).__init__(context, request)

    @lbr_view_config(route_name='external_serial_code_settings.index',
                     renderer='altair.app.ticketing:templates/external_serial_code/settings/index.html')
    def index(self):
        settings = paginate.Page(
            self.context.settings,
            page=int(self.request.params.get('page', 0)),
            items_per_page=50,
            url=PageURL_WebOb_Ex(self.request)
        )
        return {
            'settings': settings
        }

    @lbr_view_config(route_name='external_serial_code_settings.show',
                     renderer='altair.app.ticketing:templates/external_serial_code/settings/show.html')
    def show(self):
        if not self.context.setting:
            raise HTTPNotFound

        return {
            'setting': self.context.setting
        }

    @lbr_view_config(route_name='external_serial_code_settings.new',
                     renderer='altair.app.ticketing:templates/external_serial_code/settings/index.html')
    def new(self):
        settings = paginate.Page(
            self.context.settings,
            page=int(self.request.params.get('page', 0)),
            items_per_page=50,
            url=PageURL_WebOb_Ex(self.request)
        )
        return {
            'settings': settings
        }

    @lbr_view_config(route_name='external_serial_code_settings.edit',
                     renderer='altair.app.ticketing:templates/external_serial_code/settings/index.html')
    def edit(self):
        settings = paginate.Page(
            self.context.settings,
            page=int(self.request.params.get('page', 0)),
            items_per_page=50,
            url=PageURL_WebOb_Ex(self.request)
        )
        return {
            'settings': settings
        }

    @lbr_view_config(route_name='external_serial_code_settings.delete',
                     renderer='altair.app.ticketing:templates/external_serial_code/settings/index.html')
    def delete(self):
        settings = paginate.Page(
            self.context.settings,
            page=int(self.request.params.get('page', 0)),
            items_per_page=50,
            url=PageURL_WebOb_Ex(self.request)
        )
        return {
            'settings': settings
        }
