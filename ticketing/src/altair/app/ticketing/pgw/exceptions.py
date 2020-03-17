# encoding: utf-8

class PgwAPIError(Exception):
    def __init__(self, error_code, error_message, payment_id):
        self.error_code = error_code
        self.error_message = error_message
        self.payment_id = payment_id

