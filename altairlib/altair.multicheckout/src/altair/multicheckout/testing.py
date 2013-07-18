from pyramid import testing

class DummyCheckout3D(object):
    def __init__(self, CmnErrorCd='000000'):
        self.CmnErrorCd = CmnErrorCd

    def secure3d_enrol(self, order_no, enrol):
        return testing.DummyModel(
            OrderNo=order_no,
            CmnErrorCd=self.CmnErrorCd,
            )

    def secure3d_auth(self, order_no, auth):
        return testing.DummyModel(
            OrderNo=order_no,
            CmnErrorCd=self.CmnErrorCd,
            )
    
    def request_card_auth(self, order_no, card_auth):
        return testing.DummyModel(
            OrderNo=order_no,
            CmnErrorCd=self.CmnErrorCd,
            )

    def request_card_sales(self, order_no):
        return testing.DummyModel(
            OrderNo=order_no,
            CmnErrorCd=self.CmnErrorCd,
            )

    def request_card_cancel_auth(self, order_no):
        return testing.DummyModel(
            OrderNo=order_no,
            CmnErrorCd=self.CmnErrorCd,
            )

    def request_card_sales_part_cancel(self, order_no, params):
        return testing.DummyModel(
            OrderNo=order_no,
            CmnErrorCd=self.CmnErrorCd,
            )

    def request_card_cancel_sales(self, order_no):
        return testing.DummyModel(
            OrderNo=order_no,
            CmnErrorCd=self.CmnErrorCd,
            )

    def request_card_inquiry(self, order_no):
        return testing.DummyModel(
            OrderNo=order_no,
            CmnErrorCd=self.CmnErrorCd,
            )


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

    def HTTPConnection(self, host, port):
        self.host = host
        self.port = port
        self.called.append(('HTTPConnection', [host, port]))
        return self

    def HTTPSConnection(self, host, port):
        self.host = host
        self.port = port
        self.called.append(('HTTPSConnection', [host, port]))
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
