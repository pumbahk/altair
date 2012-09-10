# -*- coding:utf-8 -*-
import logging
from pyramid.view import view_config, render_view_to_response
from . import schemas
logger = logging.getLogger(__name__)

class OrderReviewView(object):

    def __init__(self, request):
        self.request = request
        self.context = request.context

    def __call__(self):
        return dict()

    def get(self):
        form = schemas.OrderReviewSchema(self.request.params)
        response = render_view_to_response(form, self.request, name="order_review_form")
        if response is None:
            raise ValueError
        return response

    @property
    def order_not_found_message(self):
        return [u'受付番号または電話番号が違います。']

    def post(self):
        form = schemas.OrderReviewSchema(self.request.params)
        if not form.validate():
            response = render_view_to_response(form, self.request, name="order_review_form")
            if response is None:
                raise ValueError
            return response

        order, sej_order = self.context.get_order()
        if not order or \
           order.shipping_address is None or ( \
           order.shipping_address.tel_1 != form.data.get('tel') and \
           order.shipping_address.tel_2 != form.data.get('tel')):

            self.request.errors = form.errors
            self.request.errors['order_no'] = self.order_not_found_message

            response = render_view_to_response(form, self.request, name="order_review_form")
            if response is None:
                raise ValueError
            return response

        else:
            return dict(order=order, sej_order=sej_order, shipping_address=order.shipping_address)

@view_config(name="order_review_form")
def order_review_form_view(form, request):
    return dict(form=form)

def exception_view(context, request):
    logger.error("The error was: %s" % context, exc_info=request.exc_info)
    return dict()

def notfound_view(context, request):
    logger.error("The error was: %s" % context, exc_info=request.exc_info)
    return dict()

@view_config(name="contact")
def contact_view(context, request):
    return dict()
