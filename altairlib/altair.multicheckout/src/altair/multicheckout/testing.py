from pyramid import testing

class DummyCheckout3D(object):
    def __init__(self, CmnErrorCd=u'000000', ErrorCd=u'000000', RetCd=u''):
        self.CmnErrorCd = CmnErrorCd
        self.ErrorCd = ErrorCd
        self.RetCd = RetCd

    def secure3d_enrol(self, response_factory, order_no, enrol):
        resp = response_factory.create_secure3d_req_enrol_response()
        resp.ErrorCd = self.ErrorCd
        resp.RetCd = self.RetCd
        return resp

    def secure3d_auth(self, response_factory, order_no, auth):
        resp = response_factory.create_secure3d_auth_response()
        resp.ErrorCd = self.ErrorCd
        resp.RetCd = self.RetCd
        return resp
    
    def request_card_auth(self, response_factory, order_no, card_auth):
        resp = response_factory.create_multicheckout_response_card()
        resp.OrderNo = order_no
        resp.CmnErrorCd = self.CmnErrorCd
        return resp

    def request_card_sales(self, response_factory, order_no):
        resp = response_factory.create_multicheckout_response_card()
        resp.OrderNo = order_no
        resp.CmnErrorCd = self.CmnErrorCd
        return resp

    def request_card_cancel_auth(self, response_factory, order_no):
        resp = response_factory.create_multicheckout_response_card()
        resp.OrderNo = order_no
        resp.CmnErrorCd = self.CmnErrorCd
        return resp

    def request_card_sales_part_cancel(self, response_factory, order_no, params):
        resp = response_factory.create_multicheckout_response_card()
        resp.OrderNo = order_no
        resp.CmnErrorCd = self.CmnErrorCd
        return resp

    def request_card_cancel_sales(self, response_factory, order_no):
        resp = response_factory.create_multicheckout_response_card()
        resp.OrderNo = order_no
        resp.CmnErrorCd = self.CmnErrorCd
        return resp

    def request_card_inquiry(self, response_factory, order_no):
        resp = response_factory.create_multicheckout_inquiry_response_card()
        resp.OrderNo = order_no
        resp.CmnErrorCd = self.CmnErrorCd
        return resp


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
        from altair.multicheckout import models
        self.called.append(('secure3d_auth', args, kwargs))
        return models.Secure3DAuthResponse(ErrorCd=self.ErrorCd, RetCd=self.RetCd, Xid=self.Xid, Ts=self.Ts, Cavva=self.Cavva, Cavv=self.Cavv, Eci=self.Eci, Mvn=self.Mvn)

    def is_enable_auth_api(self, *args, **kwargs):
        self.called.append(('is_enable_auth_api', args, kwargs))
        return self.enable_auth_api

    def is_enable_secure3d(self, *args, **kwargs):
        self.called.append(('is_enable_secure3d', args, kwargs))
        return True

    def request_card_auth(self, *args, **kwargs):
        from altair.multicheckout import models
        self.called.append(('request_card_auth', args, kwargs))
        return models.MultiCheckoutResponseCard(ApprovalNo=self.ApprovalNo)


class DummyHTTPLib(object):
    def __init__(self, response_body, status=200, reason="OK"):
        self.called = []
        self.response_body = response_body
        self.status = status
        self.reason = reason
        from io import BytesIO
        self.response_body = BytesIO(self.response_body)

    def HTTPConnection(self, host, port, timeout=None):
        self.host = host
        self.port = port
        self.called.append(('HTTPConnection', [host, port]))
        self.timeout = timeout
        return self

    def HTTPSConnection(self, host, port, timeout=None):
        self.host = host
        self.port = port
        self.called.append(('HTTPSConnection', [host, port]))
        self.timeout = timeout
        return self

    def request(self, method, path, body, headers):
        self.method = method
        self.path = path
        self.body = body
        self.headers = headers
        self.called.append(('request', [method, path, body, headers]))

    def getresponse(self):
        self.called.append(('getresponse', []))
        return self

    def read(self, block=-1):
        self.called.append(('read', [block]))
        return self.response_body.read(block)

    def close(self):
        self.called.append(('close', []))
        self.response_body.close()

class DummyMultichekoutSettingFactory(object):
    def __init__(self, result):
        self.result = result

    def __call__(self, request, override_name):
        return self.result
