from pyramid import testing
from webob.multidict import MultiDict 

class DummyRequest(testing.DummyRequest):
    def __init__(self, *args, **kwargs):
        super(DummyRequest, self).__init__(*args, **kwargs)

        for attr in ("POST", "GET", "params"):
            if hasattr(self, attr):
                setattr(self, attr, MultiDict(getattr(self, attr)))


def dummy_form_factory(name="DummyForm", validate=False, errors=None):
    def _validate(self):
        return validate

    def __init__(self, *args, **kwargs):
        self._args=args
        self._kwargs=kwargs

    attrs = dict(errors= errors or {"error1": "error-is-occured"}, 
                 validate = _validate, 
                 __init__=__init__)
    return type(name, (object, ), attrs)
