# -*- coding: utf-8 -*-
from zope.interface import Interface, Attribute, implements
from zope.interface.verify import verifyObject
from pyramid.interfaces import IView, IRoutesMapper, IRouteRequest, IViewClassifier, IMultiView
from pyramid.security import Allow, Everyone, Authenticated, authenticated_userid

from ticketing.operators.models import OperatorAuth, OperatorRole, Operator

import sqlahelper
session = sqlahelper.get_session()

def newRootFactory(exemption_matcher):
    acl = [
        (Allow, Everyone        , 'everybody'),
        (Allow, Authenticated   , 'authenticated'),
        (Allow, 'login'         , 'everybody'),
        (Allow, 'api'           , 'api'),
        ]

    # build ACL
    roles = OperatorRole.all()
    for role in roles:
        for permission in role.permissions:
            acl.append((Allow, role.name, permission.category_name))

    class Root(object):
        # the same ACL is applied to every resource under.
        __acl__ = acl

        def __init__(self, request):
            if exemption_matcher(request):
                return None
            user_id = authenticated_userid(request)
            # assign the operator object to the context
            self.user = Operator.get_by_login_id(user_id) if user_id is not None else None
            self.organization = self.user and self.user.organization
            self.request = request

            # route_name:permission のリストを生成し、ビューでのリンク生成時に権限有無の確認につかう
            registry = self.request.registry
            route_permission = getattr(registry, 'route_permission', None)
            if not route_permission:
                self.mapper = registry.queryUtility(IRoutesMapper)
                if self.mapper:
                    route_permission = {}
                    routes = self.mapper.get_routes()
                    for route in routes:
                        request_iface = registry.queryUtility(IRouteRequest, name=route.name)
                        if request_iface:
                            view_callable = registry.adapters.lookup(
                                (IViewClassifier, request_iface, Interface), IView, name='', default=None
                            )
                            if IMultiView.providedBy(view_callable):
                                permissions = []
                                for order, view, phash in view_callable.get_views(request):
                                    permissions.append(getattr(view, '__permission__', None))
                                permissions = list(set(permissions))
                                if len(permissions) == 1:
                                    route_permission[route.name] = permissions[0]
                                else:
                                    route_permission[route.name] = permissions
                            else:
                                route_permission[route.name] = getattr(view_callable, '__permission__', None)
                    registry.route_permission = route_permission

    return Root

def groupfinder(userid, request):
    user = session.query(Operator).join(OperatorAuth).filter(OperatorAuth.login_id == userid).first()
    if user is None:
        return []
    return [role.name for role in user.roles]

class ActingAsBreadcrumb(Interface):
    navigation_parent = Attribute('')
    navigation_name = Attribute('')

class Titled(Interface):
    title = Attribute('')
