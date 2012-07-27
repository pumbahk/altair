import logging
logger = logging.getLogger(__file__)

from pyramid.view import view_config, view_defaults
from ticketing.views import BaseView
from pyramid.renderers import render_to_response
from pyramid.httpexceptions import HTTPFound, HTTPError

from pyramid.url import route_path
from pyramid.security import authenticated_userid, forget

from ticketing.oauth2.models import Service, AccessToken
#from forms import AuthorizeForm
from ticketing.oauth2.authorize import Authorizer, MissingRedirectURI, AuthorizationException
from ticketing.operators.models import Operator
from ..core import models as c_models
from sqlalchemy.orm import joinedload

import sqlahelper
session = sqlahelper.get_session()

@view_config(route_name='api.access_token' , renderer='json')
def access_token(context, request):
    service_key = request.GET.get("client_id")
    token_key = request.GET.get("code")

    logger.info("*api login* get api access token: service_key: %s, token_key: %s" % (service_key, token_key))

    client = Service.get_key(service_key)
    token = AccessToken.get_by_key(token_key)

    if token and client:
        operator = token.operator
        params = {
            'access_token'  : token.token,
            'user_id'       : operator.id,
            'roles'         : [role.name for role in operator.roles],
            'organization_id'     : operator.organization.id,
            'organization_name'   : operator.organization.name,
            'screen_name'   : operator.name,
        }
        logger.info("*api login* return api access token: %s" % params)
        return params
    else:
        return {}

@view_config(route_name="api.forget_loggedin")
def forget_loggedin(request):
    ## todo: added default failback.
    ## todo: need some validation.
    return_url = request.params.get("return_to", "/default-fail-back-path")
    logger.info("*api logout* logout from external site. return to: %s" % return_url)
    headers = forget(request)
    return HTTPFound(location=return_url, headers=headers)

# TODO move to oauth2
@view_defaults(permission='authenticated')
class LoginOAuth(BaseView):

    @view_config(route_name='login.authorize')
    def authorize(self):
        login_id = authenticated_userid(self.request)
        operator = Operator.get_by_login_id(login_id)

        user = self.context.user
        authorizer = Authorizer()

        logger.info("*api login* authorize request params %s" % dict(self.request.params))

        try:
            authorizer.validate(self.request, self.context)
        except MissingRedirectURI, e:
            return HTTPFound(location=self.request.route_url("login.missing_redirect_url"))
        except AuthorizationException, e:
            return authorizer.error_redirect()

        redirect_url = None
        if self.request.method == 'GET':
            if user:
                redirect_url = authorizer.grant_redirect()
            else:
                redirect_url = HTTPError()
        else:
            redirect_url = HTTPFound(location="/")
        logger.info("*api login* authorize redirect url: status:%s location:%s" % (redirect_url.status, redirect_url.location))
        return redirect_url

@view_defaults(permission="api")
class StockStatus(BaseView):
    @view_config(route_name='api.stock_statuses_for_event', request_method="GET", renderer='json')
    def stock_statuses(self):
        event_id = self.request.matchdict.get('event_id')
        stocks = session.query(c_models.Stock) \
            .options(joinedload(c_models.Stock.stock_status), joinedload(c_models.Stock.stock_type), joinedload(c_models.Stock.performance)) \
            .join(c_models.ProductItem.stock) \
            .join(c_models.ProductItem.product) \
            .join(c_models.Product.event) \
            .join(c_models.Stock.stock_holder) \
            .join(c_models.StockHolder.account) \
            .join(c_models.Event.organization) \
            .filter(c_models.Product.event_id == event_id) \
            .filter(c_models.Account.user_id == c_models.Organization.user_id) \
            .distinct(c_models.Stock.id) \
            .order_by(c_models.Stock.id) \
            .all()
        return dict(
            performances=[
                dict(
                    id=performance.id,
                    name=performance.name,
                    start_on=performance.start_on and performance.start_on.isoformat(),
                    end_on=performance.end_on and performance.end_on.isoformat()
                    )
                    for performance in dict((stock.performance_id, stock.performance) for stock in stocks).values()
                ],
            stock_types=[
                dict(
                    id=stock_type.id,
                    name=stock_type.name
                    )
                    for stock_type in dict((stock.stock_type.id, stock.stock_type) for stock in stocks).values()
                ],
            stocks=[
                dict(
                    id=stock.id,
                    stock_type_id=stock.stock_type_id,
                    performance_id=stock.performance_id,
                    assigned=stock.quantity,
                    available=stock.stock_status.quantity
                    )
                for stock in stocks
                ]
            )
