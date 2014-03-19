#-*- coding: utf-8 -*-
class DuplicateNameError(Exception):
    pass

class RequestAccessor(object):
    in_params = {}
    in_matchdict = {}

    def __init__(self, request):
        self._validate()
        self._request = request

    def _validate(self):
        names = self._in_matchdict.keys() + self._in_params.keys()
        uniq_names = set(names)
        error_names = [name for name in uniq_names if 1 != names.count(name)]
        if error_names:
            raise DuplicateNameError('Duplicate installed: {}'.format(error_names))

    def __getattr__(self, name):
        pass
