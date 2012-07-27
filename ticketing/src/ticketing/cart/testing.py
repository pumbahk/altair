from zope.interface import implementer
from ..checkout import interfaces
from pyramid import testing
from ..testing import _setup_db, _teardown_db

@implementer(interfaces.ISigner)
class DummySigner(object):
    def __init__(self, sign_result):
        self.sign_result = sign_result
        self.called = []

    def __call__(self, target):
        self.called.append(target)
        return self.sign_result

class DummyRequest(testing.DummyRequest):
    def __init__(self, *args, **kwargs):
        super(DummyRequest, self).__init__(*args, **kwargs)
        from webob.multidict import MultiDict
        if hasattr(self, 'params'):
            self.params = MultiDict(self.params)

class DummySecure3D(object):
    def __init__(self, AcsUrl, PaReq, Md, enable_auth_api=True,
                 mvn=None, xid=None, ts=None, eci=None, cavv=None, cavva=None,
                 order_no=None, status=None, public_tran_id=None,
                 ahead_com_cd=None, approval_no=None, card_error_cd=None, req_ymd=None, cmd_error_cd=None, error_cd=None, ret_cd=None):

        self.called = []
        self.AcsUrl = AcsUrl
        self.PaReq = PaReq
        self.Md = Md
        self.enable_auth_api = enable_auth_api

        self.Mvn = mvn
        self.Xid = xid
        self.Ts = ts
        self.Eci = eci
        self.Cavv = cavv
        self.Cavva = cavva
        self.ErrorCd = error_cd

        self.RetCd = ret_cd

        self.OrderNo = order_no
        self.Status = status
        self.PublicTranId=public_tran_id
        self.AheadComCd=ahead_com_cd
        self.ApprovalNo=approval_no
        self.CardErrorCd=card_error_cd
        self.ReqYmd=req_ymd
        self.CmnErrorCd=cmd_error_cd

    def secure3d_enrol(self, *args, **kwargs):
        self.called.append(('secure3d_enrol', args, kwargs))
        return self

    def secure3d_auth(self, *args, **kwargs):
        from ..multicheckout import models
        self.called.append(('secure3d_auth', args, kwargs))
        return models.Secure3DAuthResponse(ErrorCd=self.ErrorCd, RetCd=self.RetCd, Xid=self.Xid, Ts=self.Ts, Cavva=self.Cavva, Cavv=self.Cavv, Eci=self.Eci, Mvn=self.Mvn)

    def is_enable_auth_api(self, *args, **kwargs):
        self.called.append(('is_enable_auth_api', args, kwargs))
        return self.enable_auth_api

    def is_enable_secure3d(self, *args, **kwargs):
        self.called.append(('is_enable_secure3d', args, kwargs))
        return True

    def request_card_auth(self, *args, **kwargs):
        from ..multicheckout import models
        self.called.append(('request_card_auth', args, kwargs))
        return models.MultiCheckoutResponseCard(ApprovalNo=self.ApprovalNo)
