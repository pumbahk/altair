# -*- coding:utf-8 -*-
import sqlahelper
import transaction
from altair.sqlahelper import get_db_session
from pyramid.httpexceptions import HTTPNotFound
from pyramid.interfaces import IRoutesMapper
from pyramid.security import authenticated_userid
from altair.app.ticketing.operators.models import Operator, OperatorAuth
import logging


logger = logging.getLogger(__name__)


def can_route(request, registry, user_id):
    session = get_db_session(request, 'slave')
    operator = session.query(Operator).join(OperatorAuth).filter(OperatorAuth.login_id == user_id).first()

    if not operator or not operator.route_group:
        return True

    mapper = registry.queryUtility(IRoutesMapper)
    request.environ['PATH_INFO'] = request.path_info
    info = mapper(request)

    if info['route']:
        current_route_name = info['route'].name
    else:
        # ルートが見つからない場合は、jsやcssなどのアセットが来ているためそのまま通す
        return True

    # OperatorRouteGroupに制限されたユーザの場合、このルートしか通れない
    for route in operator.route_group.operator_routes:
        if route.route_name == current_route_name:
            return True
    return False


def route_restriction_factory(handler, registry):
    def tween(request):
        try:
            transaction.commit()
            user_id = authenticated_userid(request)
            if user_id:
                if can_route(request, registry, user_id):
                    # ルートが限定されない場合
                    return handler(request)

                # ルートを限定された場合、これ以降通さない
                return HTTPNotFound()
            else:
                return handler(request)
        except Exception as e:
            logger.error('[TWE001] Failed route restriction. message=%s', e.message, exc_info=1)
    return tween


def session_cleaner_factory(handler, registry):
    def tween(request):
        sqlahelper.get_session().remove()
        try:
            return handler(request)
        finally:
            sqlahelper.get_session().remove()
    return tween
