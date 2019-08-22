# -*- coding: utf-8 -*-
from ..exc import FamiPortError


class FamiPortRequestTypeError(FamiPortError):
    pass


class FamiPortResponseBuilderLookupError(FamiPortError):
    pass


class FamiPortInvalidResponseError(FamiPortError):
    pass


class FamiEncodeError(Exception):
    pass

class FDCAPIError(Exception):
    pass