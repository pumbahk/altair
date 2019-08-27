# -*- coding: utf-8 -*-
from ..exc import FamiPortError


class FamiPortRequestTypeError(FamiPortError):
    pass


class FamiPortResponseBuilderLookupError(FamiPortError):
    pass


class FamiPortInvalidResponseError(FamiPortError):
    pass


class FamiEncodeError(Exception):
    """券面で使用不可な文字がある時Exceptionを投げます。"""
    pass


class FDCAPIError(Exception):
    pass