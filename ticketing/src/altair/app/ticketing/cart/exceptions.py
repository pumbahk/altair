# encoding: utf-8
from pyramid.decorator import reify
from altair.sqlahelper import get_db_session
from sqlahelper import get_session as get_default_db_session

class InvalidCSRFTokenException(Exception):
    pass

class CartException(Exception):
    pass

class NoCartError(CartException):
    pass

class NoEventError(CartException):
    pass

class NoPerformanceError(CartException):
    pass

class TooManyCartsCreated(CartException):
    def __init__(self, id_=None):
        self.id_ = id_

class OverQuantityLimitError(CartException):
    def __init__(self, upper_limit):
        super(OverQuantityLimitError, self).__init__()
        self.upper_limit = upper_limit

class ZeroQuantityError(CartException):
    pass

class InvalidCartStatusError(CartException):
    def __init__(self, *args, **kwargs):
        cart_id = kwargs.pop('cart_id')
        super(CartException, self).__init__(*args, **kwargs)
        self.cart_id = cart_id

class ContextualCartException(CartException):
    class Nothing(object):
        pass

    not_provided = Nothing()

    def __init__(self, request, message, event_id=None, performance_id=None, sales_segment_group_id=None, sales_segment_id=None, **kwargs):
        super(ContextualCartException, self).__init__(message)
        self.request = request
        self.event_id = event_id
        self.performance_id = performance_id
        self.sales_segment_group_id = sales_segment_group_id
        self.sales_segment_id = sales_segment_id

    @classmethod
    def from_resource(cls, context, request, message='', event_id=not_provided, performance_id=not_provided, sales_segment_id=not_provided, **kwargs):
        if event_id is cls.not_provided:
            try:
                event_id = context.event.id
            except:
                event_id = None
        if performance_id is cls.not_provided:
            try:
                performance_id = context.performance.id
            except:
                performance_id = None
        if sales_segment_id is cls.not_provided:
            try:
                sales_segment_id = context.sales_segment.id
            except:
                sales_segment_id = None
        return cls(
            request,
            message,
            event_id=event_id,
            performance_id=performance_id,
            sales_segment_id=sales_segment_id,
            **kwargs
            )

    # do not reify this
    @property
    def session(self):
        try:
            return get_db_session(self.request, 'exc')
        except Exception:
            return get_default_db_session()

    @reify
    def event(self):
        from altair.app.ticketing.core.models import Event
        if self.event_id is None:
            if self.performance is not None:
                return self.performance.event
            elif self.sales_segment_group is not None:
                return self.sales_segment_group.event
            else:
                return None
        else:
            return self.session.query(Event).filter_by(id=self.event_id).first()

    @reify
    def performance(self):
        from altair.app.ticketing.core.models import Performance
        if self.performance_id is None:
            if self.sales_segment is not None:
                return self.sales_segment.performance
            else:
                return None
        else:
            return self.session.query(Performance).filter_by(id=self.performance_id).first()

    @reify
    def sales_segment(self):
        from altair.app.ticketing.core.models import SalesSegment
        return self.session.query(SalesSegment).filter_by(id=self.sales_segment_id).first()

    @reify
    def sales_segment_group(self):
        from altair.app.ticketing.core.models import SalesSegmentGroup
        return self.session.query(SalesSegmentGroup).filter_by(id=self.sales_segment_group_id).first()

class NoSalesSegment(ContextualCartException):
    pass

class OutTermSalesException(ContextualCartException):
    """ 期限外の販売区分に対するアクセス"""
    def __init__(self, *args, **kwargs):
        next = kwargs.pop('next')
        last = kwargs.pop('last')
        type_ = kwargs.pop('type_', None)
        super(OutTermSalesException, self).__init__(*args, **kwargs)
        self.next = next
        self.last = last
        self.type_ = type_

class CartCreationException(ContextualCartException):
    pass

class DeliveryFailedException(ContextualCartException):
    def __init__(self, *args, **kwargs):
        order_no = kwargs.pop('order_no')
        super(DeliveryFailedException, self).__init__(*args, **kwargs)
        self.order_no = order_no

class OverOrderLimitException(ContextualCartException):
    def __init__(self, *args, **kwargs):
        order_limit = kwargs.pop('order_limit')
        super(OverOrderLimitException, self).__init__(*args, **kwargs)
        self.order_limit = order_limit

class PaymentMethodEmptyError(ContextualCartException):
    pass
