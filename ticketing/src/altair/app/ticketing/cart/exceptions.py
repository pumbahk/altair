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

class AuthenticationError(CartException):
    pass

class DeletedProductError(CartException):
    pass


class DifferentPdmpError(CartException):
    pass

class XSSAtackCartError(CartException):
    pass


class ChangedProductPriceError(CartException):
    back_url = None

    def __init__(self, back_url):
        self.back_url = back_url


class DiscountCodeConfirmError(CartException):
    pass


class DiscountCodeInternalError(CartException):
    pass


class OwnDiscountCodeDuplicateError(CartException):
    pass


class NotExistingOwnDiscountCodeError(CartException):
    pass


class NotAllowedBenefitUnitError(CartException):
    pass


class TooManyCartsCreated(CartException):
    def __init__(self, id_=None):
        super(TooManyCartsCreated, self).__init__()
        self.id_ = id_

class QuantityOutOfBoundsError(CartException):
    def __init__(self, quantity_given, min_quantity, max_quantity):
        super(QuantityOutOfBoundsError, self).__init__()
        self.quantity_given = quantity_given
        self.min_quantity = min_quantity
        self.max_quantity = max_quantity

class ProductQuantityOutOfBoundsError(CartException):
    def __init__(self, quantity_given, min_product_quantity, max_product_quantity):
        super(ProductQuantityOutOfBoundsError, self).__init__()
        self.quantity_given = quantity_given
        self.min_quantity = min_product_quantity
        self.max_quantity = max_product_quantity

class PerStockTypeQuantityOutOfBoundsError(CartException):
    def __init__(self, quantity_given, min_quantity, max_quantity):
        super(PerStockTypeQuantityOutOfBoundsError, self).__init__()
        self.quantity_given = quantity_given
        self.min_quantity = min_quantity
        self.max_quantity = max_quantity

class PerStockTypeProductQuantityOutOfBoundsError(CartException):
    def __init__(self, quantity_given, min_product_quantity, max_product_quantity):
        super(PerStockTypeProductQuantityOutOfBoundsError, self).__init__()
        self.quantity_given = quantity_given
        self.min_quantity = min_product_quantity
        self.max_quantity = max_product_quantity

class PerProductProductQuantityOutOfBoundsError(CartException):
    def __init__(self, quantity_given, min_product_quantity, max_product_quantity):
        super(PerProductProductQuantityOutOfBoundsError, self).__init__()
        self.quantity_given = quantity_given
        self.min_quantity = min_product_quantity
        self.max_quantity = max_product_quantity

class InvalidCartStatusError(CartException):
    def __init__(self, cart_id):
        super(InvalidCartStatusError, self).__init__()
        self.cart_id = cart_id

class ContextualCartException(CartException):
    class Nothing(object):
        pass

    not_provided = Nothing()

    def __init__(self, request, message, event_id=None, performance_id=None, sales_segment_group_id=None, sales_segment_id=None, authenticated_user=None, host_base_url=None, **kwargs):
        super(ContextualCartException, self).__init__(message)
        self.request = request
        self.event_id = event_id
        self.performance_id = performance_id
        self.sales_segment_group_id = sales_segment_group_id
        self.sales_segment_id = sales_segment_id
        self.authenticated_user = authenticated_user
        self.host_base_url = host_base_url

    @classmethod
    def from_resource(cls, context, request, message='', event_id=not_provided, performance_id=not_provided, sales_segment_id=not_provided, authenticated_user=not_provided, host_base_url=not_provided, **kwargs):
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
        if authenticated_user is cls.not_provided:
            try:
                authenticated_user = context.authenticated_user
            except:
                authenticated_user = None
        if host_base_url is cls.not_provided:
            try:
                host_base_url = context.host_base_url
            except:
                host_base_url = None
        return cls(
            request,
            message,
            event_id=event_id,
            performance_id=performance_id,
            sales_segment_id=sales_segment_id,
            authenticated_user=authenticated_user,
            host_base_url=host_base_url,
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


class OverOrderLimitException(ContextualCartException):
    def __init__(self, *args, **kwargs):
        order_limit = kwargs.pop('order_limit')
        is_spa_cart = kwargs.pop('is_spa_cart')
        super(OverOrderLimitException, self).__init__(*args, **kwargs)
        self.order_limit = order_limit
        self.is_spa_cart = is_spa_cart


class OverQuantityLimitException(ContextualCartException):
    def __init__(self, *args, **kwargs):
        quantity_limit = kwargs.pop('quantity_limit')
        is_spa_cart = kwargs.pop('is_spa_cart')
        super(OverQuantityLimitException, self).__init__(*args, **kwargs)
        self.quantity_limit = quantity_limit
        self.is_spa_cart = is_spa_cart


class PaymentMethodEmptyError(ContextualCartException):
    pass


class PaymentError(ContextualCartException):
    def __init__(self, *args, **kwargs):
        cause = kwargs.pop('cause')
        super(PaymentError, self).__init__(*args, **kwargs)
        self.cause = cause
        # Point API レスポンスの result_code リスト
        self.point_result_code = kwargs.pop('point_result_code', list())


class CompletionPageNotRenderered(CartException):
    pass


class OAuthRequiredSettingError(Exception):
    pass


class NotSpaCartAllowedException(Exception):
    pass
