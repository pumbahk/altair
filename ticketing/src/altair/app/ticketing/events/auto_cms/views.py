# -*- coding: utf-8 -*-

import logging
from pyramid.view import view_config, view_defaults
from altair.app.ticketing.views import BaseView
from altair.app.ticketing.fanstatic import with_bootstrap
from .forms import ImageUploadForm
logger = logging.getLogger(__name__)


@view_defaults(decorator=with_bootstrap, permission='sales_viewer')
class AutoCmsImage(BaseView):

    @view_config(route_name='auto_cms.image.index', request_method='GET',
                 renderer='altair.app.ticketing:templates/auto_cms/image/index.html')
    def index(self):
        return dict(
            event=self.context.event
        )

    @view_config(route_name='auto_cms.image.edit', request_method='GET',
                 renderer='altair.app.ticketing:templates/auto_cms/image/edit.html')
    def edit_get(self):
        return dict(
            form=ImageUploadForm(),
            performance=self.context.performance
        )

    @view_config(route_name='auto_cms.image.edit', request_method='POST',
                 renderer='altair.app.ticketing:templates/auto_cms/image/edit.html')
    def edit_post(self):
        form = ImageUploadForm(self.request.POST)

        if not form.validate():
            return dict(
                form=form,
                performance=self.context.performance
            )
        self.context.save_upload_file([self.context.performance])
        self.request.session.flash(u"画像を保存しました")
        return dict(
            form=form,
            performance=self.context.performance
        )

    @view_config(route_name='auto_cms.image.all_edit', request_method='GET',
                 renderer='altair.app.ticketing:templates/auto_cms/image/all_edit.html')
    def all_edit_get(self):
        return dict(
            form=ImageUploadForm(),
            event=self.context.event
        )

    @view_config(route_name='auto_cms.image.all_edit', request_method='POST',
                 renderer='altair.app.ticketing:templates/auto_cms/image/all_edit.html')
    def all_edit_post(self):
        form = ImageUploadForm(self.request.POST)

        if not form.validate():
            return dict(
                form=form,
                event=self.context.event
            )
        self.context.save_upload_file(self.context.event.performances)
        self.request.session.flash(u"画像を保存しました")
        return dict(
            form=form,
            event=self.context.event
        )
