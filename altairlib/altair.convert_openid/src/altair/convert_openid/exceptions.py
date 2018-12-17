# -*- coding: utf-8 -*-

class ConverterAPIError(Exception):
    """
    OpenIDの転換API関連の予期せぬ例外や
    返却結果の解析時に発生したイレギュラーな例外クラスです。
    """
    pass

class EasyIDNotFoundError(Exception):
    """
    OpenIDの転換APIからEasyIDが取得できなかった祭の例外クラスです。
    レスポンスは正しく返却されているので、OpenIDが不正または誤っているなどの原因が考えられます。
    """
    pass
