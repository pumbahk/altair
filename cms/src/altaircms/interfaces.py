from zope.interface import Interface
from zope.interface import Attribute

class IConcrete(Interface):
    def concrete():
        pass

class INode(Interface):
    pass

class IConcreteNode(IConcrete, INode):
    def concrete(request=None, config=None, extra_context=None):
        pass

class IBlockTree(Interface):
    blocks = Attribute("blocks")

class ICacher(Interface):
    fetched = Attribute("fetched")
    scanned = Attribute("scanned")
    result = Attribute("result")

    def scan(target):
        pass

    def fetch():
        pass

class IHandleSession(Interface):
    def add(data, flush=False):
        pass

    def delete(data, flush=False):
        pass

class IUpdateData(Interface):
    def update_data(data, **params):
        """ update data with keyword paramaters.
        
        params is dictionary.
        use this method, like a update() of dictionary type.

        >>> D = {1: 2}
        >>> D.update(foo="bar")
        >>> D
        {1: 2, "foo": "bar"}
        """

class IWidget(Interface):
    type = Attribute(""" widget type e.g. image, freetext, ...""")
    template_name = Attribute("""render template name""")

# class IFromDict(Interface):
#     @classmethod
#     def from_dict(cls):
#         pass
# class IToDict(Interface):
#     def to_dict():
#         pass
# class IWithDict(IFromDict, IToDict):
#     pass

