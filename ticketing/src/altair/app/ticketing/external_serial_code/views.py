# -*- coding:utf-8 -*-
import webhelpers.paginate as paginate
from altair.app.ticketing.core.utils import PageURL_WebOb_Ex
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.views import BaseView
from altair.pyramid_dynamic_renderer import lbr_view_config
from pyramid.view import view_defaults
from pyramid.httpexceptions import HTTPNotFound
from .forms import ExternalSerialCodeSettingEditForm, ExternalSerialCodeSettingSearchForm, ExternalSerialCodeSearchForm


@view_defaults(decorator=with_bootstrap,
               permission="event_editor")
class ExternalSerialCodeSettingView(BaseView):
    def __init__(self, context, request):
        super(ExternalSerialCodeSettingView, self).__init__(context, request)

    @lbr_view_config(route_name='external_serial_code_settings.index',
                     renderer='altair.app.ticketing:templates/external_serial_code/settings/index.html')
    def index(self):
        search_form = ExternalSerialCodeSettingSearchForm(self.request.GET)
        settings = paginate.Page(
            self.context.get_settings(search_form),
            page=int(self.request.params.get('page', 0)),
            items_per_page=50,
            url=PageURL_WebOb_Ex(self.request)
        )
        return {
            'settings': settings,
            'search_form': search_form
        }

    @lbr_view_config(route_name='external_serial_code_settings.show',
                     renderer='altair.app.ticketing:templates/external_serial_code/settings/show.html')
    def show(self):
        if not self.context.setting:
            raise HTTPNotFound

        return {
            'setting': self.context.setting
        }

    @lbr_view_config(request_method='GET',
                     route_name='external_serial_code_settings.edit',
                     renderer='altair.app.ticketing:templates/external_serial_code/settings/edit.html')
    def edit_get(self):
        form = ExternalSerialCodeSettingEditForm()
        setting = self.context.setting
        form.name.data = setting.name
        form.label.data = setting.label
        form.description.data = setting.description
        form.url.data = setting.url
        form.start_at.data = setting.start_at
        form.end_at.data = setting.end_at
        return {
            'form': form
        }

    @lbr_view_config(request_method='POST',
                     route_name='external_serial_code_settings.edit',
                     renderer='altair.app.ticketing:templates/external_serial_code/settings/edit.html')
    def edit_post(self):
        form = ExternalSerialCodeSettingEditForm(self.request.POST)
        if form.validate():
            self.context.master_setting.name = form.name.data
            self.context.master_setting.label = form.label.data
            self.context.master_setting.description = form.description.data
            self.context.master_setting.url = form.url.data
            self.context.master_setting.start_at = form.start_at.data
            self.context.master_setting.end_at = form.end_at.data
            self.request.session.flash(u'設定を更新しました')

        return {
            'form': form
        }

    @lbr_view_config(request_method="GET",
                     route_name='external_serial_code_settings.delete',
                     renderer='altair.app.ticketing:templates/external_serial_code/settings/index.html')
    def delete_get(self):
        search_form = ExternalSerialCodeSettingSearchForm(self.request.GET)
        settings = paginate.Page(
            self.context.get_settings(search_form),
            page=int(self.request.params.get('page', 0)),
            items_per_page=50,
            url=PageURL_WebOb_Ex(self.request)
        )
        return {
            'settings': settings,
            'search_form': search_form
        }

    @lbr_view_config(request_method="POST",
                     route_name='external_serial_code_settings.delete',
                     renderer='altair.app.ticketing:templates/external_serial_code/settings/index.html')
    def delete_post(self):
        self.context.delete_setting()
        settings = paginate.Page(
            self.context.get_master_settings(),
            page=int(self.request.params.get('page', 0)),
            items_per_page=50,
            url=PageURL_WebOb_Ex(self.request)
        )
        return {
            'settings': settings,
            'search_form': ExternalSerialCodeSettingSearchForm()
        }


@view_defaults(decorator=with_bootstrap,
               permission="event_editor")
class ExternalSerialCodeView(BaseView):
    def __init__(self, context, request):
        super(ExternalSerialCodeView, self).__init__(context, request)

    @lbr_view_config(route_name='external_serial_code.index',
                     renderer='altair.app.ticketing:templates/external_serial_code/code/index.html')
    def index(self):
        if not self.context.setting:
            raise HTTPNotFound

        search_form = ExternalSerialCodeSearchForm(self.request.GET)
        codes = paginate.Page(
            self.context.get_codes(search_form),
            page=int(self.request.params.get('page', 0)),
            items_per_page=50,
            url=PageURL_WebOb_Ex(self.request)
        )
        return {
            'setting': self.context.setting,
            'codes': codes,
            'search_form': search_form
        }

    @lbr_view_config(request_method="GET",
                     route_name='external_serial_code.delete',
                     renderer='altair.app.ticketing:templates/external_serial_code/code/index.html')
    def delete_get(self):
        search_form = ExternalSerialCodeSearchForm(self.request.GET)
        codes = paginate.Page(
            self.context.get_codes(search_form),
            page=int(self.request.params.get('page', 0)),
            items_per_page=50,
            url=PageURL_WebOb_Ex(self.request)
        )
        return {
            'setting': self.context.setting,
            'codes': codes,
            'search_form': search_form
        }

    @lbr_view_config(request_method="POST",
                     route_name='external_serial_code.delete',
                     renderer='altair.app.ticketing:templates/external_serial_code/code/index.html')
    def delete_post(self):
        organization_id = self.context.organization.id
        if self.context.validate_delete_code():
            self.request.session.flash(u"予約があるため削除できません")
        else:
            self.context.delete_code()
            self.request.session.flash(u"削除しました")

        codes = paginate.Page(
            self.context.get_master_codes(organization_id),
            page=int(self.request.params.get('page', 0)),
            items_per_page=50,
            url=PageURL_WebOb_Ex(self.request)
        )
        return {
            'setting': self.context.setting,
            'codes': codes,
            'search_form': ExternalSerialCodeSearchForm()
        }
