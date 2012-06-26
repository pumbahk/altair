from zope.interface import Interface
from zope.interface import implementer
import os.path

class ILayoutTemplateLookUp(Interface):
    def __call__(filename):
        """lookup template instance"""

@implementer(ILayoutTemplateLookUp)
class LayoutTemplate(object):
    def __init__(self, layoutdir):
        self.layoutdir = layoutdir

    def __call__(self, filename):
        return os.path.join(self.layoutdir, filename)
    
