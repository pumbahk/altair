# -*- coding: utf-8 -*-

from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.url import route_path
from ticketing.views.login.forms import LoginForm
from ticketing.models import Operator, session

from deform.form import Form,Button
from deform.exception import ValidationFailure

from pyramid.security import authenticated_userid


@view_config(route_name='admin.index', renderer='ticketing:templates/admin/index.html', permission='admin')
def index(context, request):
    return {}