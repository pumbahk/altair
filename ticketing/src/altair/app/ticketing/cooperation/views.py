# -*- coding: utf-8 -*-
from pyramid.view import view_defaults, view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
from altair.app.ticketing.views import BaseView
from altair.app.ticketing.fanstatic import with_bootstrap

from .forms import CooperationUpdateForm, CooperationDownloadForm
GOOGLE = 'http://www.google.com'


@view_defaults(decorator=with_bootstrap, permission='event_editor')
class CooperationView(BaseView):

    @view_config(route_name='cooperation.index', request_method='GET',
                 renderer='altair.app.ticketing:templates/cooperation/index.html')
    def index(self):
        sitename_venueid = (('google', 'http://www.goolge.com'),)
        return {'sitename_venueid': sitename_venueid}
        
    def _test(self):
        res = Response()
        res.status = '200 OK'
        res.status_int = 200
        res.content_type = 'text/plain'
        res.charset = 'utf-8'
        res.headerlist = [
            ('Set-Cookie', 'abc=123'),
            ('X-My-Header', 'foo'),
            ]
        res.cache_for = 3600
        return res

    @view_config(route_name='cooperation.show', request_method='GET',
                 renderer='altair.app.ticketing:templates/cooperation/show.html')
    def show(self):
        from mock import Mock
        site = Mock()
        site.name = u'テスト'
        update_form = CooperationUpdateForm()
        download_form = CooperationDownloadForm()
        return {'site': site,
                'update_form': update_form,
                'download_form': download_form,
                'display_modal': False,
                }

    @view_config(route_name='cooperation.download', request_method='GET')
    def download(self):
        res = Response()
        res.status = '200 OK'
        res.status_int = 200
        res.content_type = 'text/plain'
        res.charset = 'utf-8'
        res.headerlist = [
            ('Set-Cookie', 'abc=123'),
            ('X-My-Header', 'foo'),
            ]
        res.cache_for = 3600
        return res

    @view_config(route_name='cooperation.update', request_method='POST',
                 renderer='altair.app.ticketing:templates/cooperation/show.html')
    def update(self):
        form = CooperationUpdateForm(self.request.params)
        display_modal = False
        if form.validate() and hasattr(form.cooperation_file.data, 'file'):
            csv_file = form.cooperation_file.data.file
        else:
            display_modal = True

        from mock import Mock
        site = Mock()
        site.name = u'テスト'
        update_form = form
        download_form = CooperationDownloadForm()
        return {'site': site,
                'update_form': update_form,
                'download_form': download_form,
                'display_modal': display_modal,
                }
