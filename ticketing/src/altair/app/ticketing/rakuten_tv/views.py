# -*- coding:utf-8 -*-
import logging
import json
import re

from altair.app.ticketing.views import BaseView
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.sqlahelper import get_db_session
from pyramid.view import view_config, view_defaults
from altair.pyramid_dynamic_renderer import lbr_view_config

from .models import RakutenTvSetting, RakutenTvSalesData

from .forms import RakutenTvSettingForm


logger = logging.getLogger(__name__)


@view_defaults(route_name='performances.rakuten_tv_setting', decorator=with_bootstrap, permission='authenticated')
class RakutenTvSettingView(BaseView):
    @view_config(route_name='performances.rakuten_tv_setting.index', request_method='GET',
                 renderer='altair.app.ticketing:templates/performances/show.html')
    def get_index(self):

        slave_session = get_db_session(self.request, name="slave")

        form = RakutenTvSettingForm()
        rts_data = slave_session.query(RakutenTvSetting).filter_by(performance_id=self.context.performance_id).first()

        if rts_data:
            form.id.data = rts_data.id
            form.available_flg.data = rts_data.available_flg
            form.rtv_endpoint_url.data = rts_data.rtv_endpoint_url
            form.release_date.data = rts_data.release_date
            form.description.data = rts_data.description

        return dict(
            tab="rakuten_tv",
            performance=self.context.target_performance,
            form=form
        )

    @view_config(route_name='performances.rakuten_tv_setting.index', request_method='POST',
                 renderer='altair.app.ticketing:templates/performances/show.html')
    def post_index(self):

        form = RakutenTvSettingForm(self.request.POST)

        if form.validate():
            setting_data = RakutenTvSetting()
            setting_data.performance_id = self.context.performance_id
            setting_data.available_flg = form.available_flg.data
            setting_data.rtv_endpoint_url = form.rtv_endpoint_url.data
            setting_data.release_date = form.release_date.data
            setting_data.description = form.description.data

            if form.id.data:
                setting_data.id = form.id.data
                setting_data.update_rakuten_tv_setting(setting_data)
            else:
                setting_data.insert_rakuten_tv_setting(setting_data)

            self.request.session.flash(u'設定を保存しました')

        return dict(
            tab="rakuten_tv",
            performance=self.context.target_performance,
            form=form
        )


@lbr_view_config(route_name="ticket_api.availability_check", renderer='json', request_method='POST')
def ticket_api_availability_check(context, request):

    error_code = None
    is_purchased = 0

    if not re.match(r'^\s*application/json\s*', request.content_type) or not re.match(r'^\s*UTF-8\s*', request.charset):
        return api_response_json(is_purchased, "ERR4002")

    x_api_key = request.registry.settings.get('rakuten_tv.x-api-key', None)

    if str(request).find(x_api_key) == -1:
        return api_response_json(is_purchased, "ERR4001")

    if request.json_body:
        post_json = json.loads(json.dumps(request.json_body))

        if post_json['performance_id'] and post_json['easy_id']:

            confirm_sql = RakutenTvSalesData.find_by_performance_id_and_easy_id(post_json['performance_id'], post_json['easy_id'])

            if confirm_sql:
                if not confirm_sql.paid_at:
                    error_code = "ERR2004"
                elif confirm_sql.canceled_at:
                    error_code = "ERR2005"
                elif confirm_sql.refunded_at:
                    error_code = "ERR2006"
                else:
                    is_purchased = 1
                    return api_response_json(is_purchased, error_code)

            else:
                error_code = "ERR2001"

        else:
            error_code = "ERR2001"

    return api_response_json(is_purchased, error_code)


def api_response_json(is_purchased, error_code):

    response_data = {
        'is_purchased': is_purchased,
        'error_code': error_code,
    }

    response_json = json.dumps(response_data)

    return response_json
