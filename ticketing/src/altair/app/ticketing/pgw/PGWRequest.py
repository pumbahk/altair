# -*- coding: utf-8 -*-


class PGWRequest(object):
    """
    PGWの各APIリクエスト用のオブジェクトを作成します
    """
    def __init__(self, payment_ids):
        self.callback_url = None
        self.card_token = None
        self.cvv_token = None
        self.email = None
        self.enrollment_id = None
        self.gross_amount = None
        self.payment_id = None
        self.payment_ids = None
        if type(payment_ids) == 'list':
            self.payment_ids = payment_ids
        else:
            self.payment_id = payment_ids
        self.search_type = None
        self.sub_service_id = None
        self.three_d_secure_authentication_result = None

    def create_authorize_request(self, email):
        """
        AuthorizeAPI用リクエストオブジェクトを作成します
        :param email: Eメールアドレス
        :return:
        """
        self.email = email
        # PGWOrderStatusの対象レコード取得
        """
        self.sub_service_id = 
        self.gross_amount = 
        self.card_token = 
        self.cvv_token =
        """

    def create_capture_request(self):
        """
        CaptureAPI用リクエストオブジェクトを作成します
        :return:
        """
        # PGWOrderStatusの対象レコード取得
        """
        self.gross_amount =
        """

    def create_authorize_and_capture_request(self, email):
        """
        AuthorizeAndCaptureAPI用リクエストオブジェクトを作成します
        :param email:
        :return:
        """
        self.email = email
        # PGWOrderStatusの対象レコード取得
        """
        self.sub_service_id = 
        self.gross_amount = 
        self.card_token = 
        self.cvv_token =
        """

    def create_find_request(self, search_type=None):
        """
        FindAPI用リクエストオブジェクトを作成します
        :param search_type:
        :return:
        """
        self.search_type = search_type

    def create_modify_request(self):
        """
        ModifyAPI用リクエストオブジェクトを作成します
        :return:
        """
        # PGWOrderStatusの対象レコード取得
        """
        self.gross_amount =
        """

    def create_three_d_secure_enrollment_check_request(self, callback_url):
        """
        3DSecureEnrollmentCheckAPI用リクエストオブジェクトを作成します
        :param callback_url:
        :return:
        """
        self.enrollment_id = '{}_E'.format(self.payment_id)
        self.callback_url = callback_url
        # PGWOrderStatusの対象レコード取得
        """
        self.sub_service_id = 
        self.gross_amount = 
        self.card_token = 
        """
