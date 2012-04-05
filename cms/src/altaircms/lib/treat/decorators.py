import venusian
from .interfaces import ICreate
from zope.interface import implementer
from altaircms.interfaces import IForm
from pyramid.interfaces import IRequest

class AsTreatSettingsBase(object):
    def __init__(self, requires=None, name=None, directive=None):
        self.requires = requires
        self.name = name
        self.directive = directive

    def callback(self, scanner, name, obj):
        implementer(ICreate)(obj)
        directive = getattr(scanner.config, self.directive)
        directive(obj, requires=self.requires, name=self.name)

    def __call__(self, cls):
        venusian.attach(cls, self.callback)
        return cls

def creator_from_form(name=None, use_request=True):
    requires = [IForm]
    if use_request:
        requires.append(IRequest)
    return AsTreatSettingsBase(requires=requires, name=name, directive="add_creator")

def updater_from_form(name=None, use_request=True):
    requires = [IForm]
    if use_request:
        requires.append(IRequest)
    return AsTreatSettingsBase(requires=requires, name=name, directive="add_updater")
