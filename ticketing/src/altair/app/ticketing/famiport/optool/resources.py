from pyramid.security import Allow, Deny, Authenticated, DENY_ALL
from pyramid.decorator import reify
from ..models import FamiPortPerformance, FamiPortReceipt
from .models import FamiPortOperator
from altair.sqlahelper import get_db_session

class BaseResource(object):
    __acl__ = [
        (Allow, Authenticated, 'authenticated'),
        (Allow, 'administrator', 'administrator'),
        (Allow, 'administrator', 'operator'),
        (Allow, 'superuser', 'administrator'),
        (Allow, 'superuser', 'operator'),
        (Allow, 'operator', 'operator'),
        DENY_ALL,
        ]

    def __init__(self, request):
        self.request = request
        if self.request.authenticated_userid:
            fami_session = get_db_session(self.request, 'famiport')
            user_id = self.request.authenticated_userid
            self.user = fami_session.query(FamiPortOperator)\
                                    .filter(FamiPortOperator.id == user_id)\
                                    .one()

    def user(self):
        return self.user

class TopResource(BaseResource):
    pass

class ExampleResource(BaseResource):
    pass

class SearchResource(BaseResource):
    pass

class DetailBaseResource(BaseResource):
    pass

class PerformanceDetailResource(DetailBaseResource):
    def __init__(self, request):
        super(ReceiptDetailResource, self).__init__(request)
        self.request = request
        fami_session = get_db_session(self.request, 'famiport')
        performance_id = self.request.matchdict.get('performance_id')
        if performance_id:
            self.performance = fami_session.query(FamiPortPerformance)\
                                           .filter(FamiPortPerformance.id == performance_id)\
                                           .one()

class RefundPerformanceDetailResource(DetailBaseResource):
    def __init__(self, request):
        super(ReceiptDetailResource, self).__init__(request)
        self.request = request
        fami_session = get_db_session(self.request, 'famiport')
        performance_id = self.request.matchdict.get('performance_id')
        if performance_id:
            self.performance = fami_session.query(FamiPortPerformance)\
                                           .filter(FamiPortPerformance.id == performance_id)\
                                           .one()

class ReceiptDetailResource(DetailBaseResource):
    def __init__(self, request):
        super(ReceiptDetailResource, self).__init__(request)
        self.request = request
        fami_session = get_db_session(self.request, 'famiport')
        receipt_id = self.request.matchdict.get('receipt_id')
        if receipt_id:
            self.receipt = fami_session.query(FamiPortReceipt)\
                                       .filter(FamiPortReceipt.id == receipt_id)\
                                       .one()

class RebookReceiptResource(BaseResource):
    def __init__(self, request):
        super(ReceiptDetailResource, self).__init__(request)
        self.request = request
        fami_session = get_db_session(self.request, 'famiport')
        self.fami_session = fami_session
        receipt_id = self.request.matchdict.get('receipt_id')
        if receipt_id:
            self.receipt = fami_session.query(FamiPortReceipt)\
                                       .filter(FamiPortReceipt.id == receipt_id)\
                                       .one()

    def update_cancel_reason(self, data):
        self.receipt.cancel_reason_code = data['cancel_reason_code']
        self.receipt.cancel_reason_text = data['cancel_reason_text']
        self.fami_session.commit()

class DetailResource(BaseResource):
    pass

class RebookResource(BaseResource):
    pass
