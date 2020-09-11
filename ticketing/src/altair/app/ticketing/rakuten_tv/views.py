# -*- coding:utf-8 -*-
import logging

from altair.app.ticketing.views import BaseView
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.sqlahelper import get_db_session
from pyramid.view import view_config, view_defaults

from .models import (
    RakutenTvSetting,
)

from .forms import (
    RakutenTvSettingForm
)


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
