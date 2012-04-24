from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.url import route_path

from ticketing.models import merge_session_with_post, record_to_appstruct, merge_and_flush
from ticketing.clients.models import Client
from ticketing.operators.models import Operator, OperatorRole, Permission

from ticketing.views import BaseView
from ticketing.fanstatic import with_bootstrap

from hashlib import md5

import webhelpers.paginate as paginate

import  sqlahelper
session = sqlahelper.get_session()

@view_defaults(decorator=with_bootstrap)
class Orders(BaseView):

    @view_config(route_name='orders.index', renderer='ticketing:templates/orders/index.html')
    def index(self):
        return {}
