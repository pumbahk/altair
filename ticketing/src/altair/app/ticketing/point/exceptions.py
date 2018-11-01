# -*- coding:utf-8 -*-


class PointAPIResponseParseException(Exception):
    """
    ポイントAPIのレスポンスXML解析時に発生する例外クラスです。
    """
    pass


class PointRedeemNoFoundException(Exception):
    """
    PointRedeemのレコードが取得できなかった際に発生する例外クラスです。
    """
    pass
