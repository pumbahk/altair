from ..tweens import IMobileRequest
from pyramid.path import caller_package

# class MobileConfigWrapper(object):
#     def __init__(self, config):
#         self.config = config

#     def add_view(self, view=None, name="", context=IMobileRequest, **kwargs):
#         self.config.add_view(view=view, name=name, context=context, **kwargs)

#     def __getattr__(self, k):
#         return getattr(self.config, k)

#     def scan(self, package=None, categories=None, onerror=None, ignore=None,
#               **kw):
#         package = self.maybe_dotted(package)
#         if package is None: # pragma: no cover
#             package = caller_package()

#         ctorkw = {'config':self}
#         ctorkw.update(kw)

#         scanner = self.venusian.Scanner(**ctorkw)
        
#         scanner.scan(package, categories=categories, onerror=onerror,
#                      ignore=ignore)

#     def with_package(self, package):
#         config = self.config.with_package(package)
#         return self.__class__(config)
