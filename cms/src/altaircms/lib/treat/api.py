# import warnings
# from zope.interface import implementer

from .interfaces import ICreate
from .interfaces import IUpdate
from altaircms.lib.apiutils import get_registry

# @implementer(ICreate)
# class DummyCreate(object):
#     @staticmethod
#     def create(*args, **kwargs):
#         warnings.warn("this is dummy create.")

def get_creator(obj, name, request=None):
    registry = get_registry(request)
    return registry.queryMultiAdapter((obj, request), ICreate, name, None)

def get_updater(obj, name, request=None):
    registry = get_registry(request)
    return registry.queryMultiAdapter((obj, request), IUpdate, name, None)

