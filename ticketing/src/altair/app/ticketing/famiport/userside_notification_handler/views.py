import logging
import json
from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.decorator import reify
from altair.app.ticketing.models import DBSession
from ..userside_models import AltairFamiPortNotification, AltairFamiPortNotificationType

logger = logging.getLogger(__name__)

@view_config(route_name='famiport.userside_api.ping')
def ping(context, request):
    return Response(content_type='text/plain', text=u'PONG')

@view_defaults(request_method='POST', renderer='json')
class FamiPortUsersideAPIView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        try:
            self.request_data = json.load(self.request.body_file)
        except ValueError:
            self.bad_request("invalid JSON data")

    @reify
    def session(self):
        return DBSession

    def bad_request(self, message):
        logger.error(message)
        raise HTTPBadRequest(body=json.dumps({"status":"error", "message":message}, encoding='UTF-8', ensure_ascii=False), content_type='application/json', charset='UTF-8')

    @view_config(route_name='famiport.userside_api.completed')
    def completed(self):
        try:
            if 'payment' in self.request_data['type']:
                if 'ticketing' in self.request_data['type']:
                    type_ = AltairFamiPortNotificationType.PaymentAndTicketingCompleted.value
                else:
                    type_ = AltairFamiPortNotificationType.PaymentCompleted.value
            else:
                if 'ticketing' in self.request_data['type']:
                    type_ = AltairFamiPortNotificationType.TicketingCompleted.value
                else:
                    self.bad_request('invalid type') 
            notification = AltairFamiPortNotification(
                type=type_,
                client_code=self.request_data['client_code'],
                order_no=self.request_data['order_no'],
                famiport_order_identifier=self.request_data['famiport_order_identifier'],
                payment_reserve_number=self.request_data['payment_reserve_number'] or None,
                ticketing_reserve_number=self.request_data['ticketing_reserve_number'] or None
                )
        except KeyError as e:
            self.bad_request("missing key: %s" % e.message)
        except TypeError as e:
            self.bad_request("invalid payload")
        self.session.add(notification)
        return {"status":"ok"}

    @view_config(route_name='famiport.userside_api.canceled')
    def canceled(self):
        try:
            if 'order' in self.request_data['type']:
                type_ = AltairFamiPortNotificationType.OrderCanceled.value
            else:
                if 'payment' in self.request_data['type']:
                    if 'ticketing' in self.request_data['type']:
                        type_ = AltairFamiPortNotificationType.PaymentAndTicketingCanceled.value
                    else:
                        type_ = AltairFamiPortNotificationType.PaymentCanceled.value
                else:
                    if 'ticketing' in self.request_data['type']:
                        type_ = AltairFamiPortNotificationType.TicketingCanceled.value
                    else:
                        self.bad_request('invalid type') 
            notification = AltairFamiPortNotification(
                type=type_,
                client_code=self.request_data['client_code'],
                order_no=self.request_data['order_no'],
                famiport_order_identifier=self.request_data.get('famiport_order_identifier', None),
                payment_reserve_number=self.request_data['payment_reserve_number'] or None,
                ticketing_reserve_number=self.request_data['ticketing_reserve_number'] or None
                )
        except KeyError as e:
            self.bad_request("missing key: %s" % e.message)
        self.session.add(notification)
        return {"status":"ok"}

    @view_config(route_name='famiport.userside_api.expired')
    def expired(self):
        try:
            notification = AltairFamiPortNotification(
                type=AltairFamiPortNotificationType.OrderExpired.value,
                client_code=self.request_data['client_code'],
                order_no=self.request_data['order_no'],
                famiport_order_identifier=self.request_data.get('famiport_order_identifier', None),
                payment_reserve_number=self.request_data['payment_reserve_number'] or None,
                ticketing_reserve_number=self.request_data['ticketing_reserve_number'] or None
                )
        except KeyError as e:
            self.bad_request("missing key: %s" % e.message)
        self.session.add(notification)
        return {"status":"ok"}

    @view_config(route_name='famiport.userside_api.refunded')
    def refunded(self):
        try:
            notification = AltairFamiPortNotification(
                type=AltairFamiPortNotificationType.Refunded.value,
                client_code=self.request_data['client_code'],
                order_no=self.request_data['order_no'],
                famiport_order_identifier=self.request_data['famiport_order_identifier'],
                payment_reserve_number=self.request_data['payment_reserve_number'] or None,
                ticketing_reserve_number=self.request_data['ticketing_reserve_number'] or None
                )
        except KeyError as e:
            self.bad_request("missing key: %s" % e.message)
        except TypeError as e:
            self.bad_request("invalid payload")
        self.session.add(notification)
        return {"status":"ok"}

