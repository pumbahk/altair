from interfaces import IAfterFormInitialize
from zope.interface import implementer 

@implementer(IAfterFormInitialize)
class AfterFormInitialize(object):
    def __init__(self, form, request, rendering_val):
        self.form = form
        self.request = request
        self.rendering_val = rendering_val
