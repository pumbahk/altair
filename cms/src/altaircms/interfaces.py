from zope.interface import Interface
from zope.interface import Attribute
from zope.interface import implementer

## 
class IForm(Interface):
    def validate():
        pass
    
class IModelEvent(Interface):
    request = Attribute("")
    obj = Attribute("")
    params = Attribute("params")

##

class IConcrete(Interface):
    def concrete():
        pass

class INode(Interface):
    pass

class IConcreteNode(IConcrete, INode):
    def concrete(request=None, config=None, extra_context=None):
        pass


class ICacher(Interface):
    fetched = Attribute("fetched")
    scanned = Attribute("scanned")
    result = Attribute("result")

    def scan(target):
        pass

    def fetch():
        pass

class IRenderable(Interface):
    def render():
        pass

## page rendering
class IStruct(Interface):
    def as_dict():
        pass
    def define(keywords, value):
        pass

class IBlockTree(Interface):
    blocks = Attribute("blocks")

## resource
class IHandleWidget(Interface):
    def _get_or_create(model, widget_id):
        pass
        
    def get_widget(widget_id):
        pass

class IHandleSession(Interface):
    def add(data, flush=False):
        pass

    def delete(data, flush=False):
        pass

class IUpdateData(Interface):
    def update_data(data, **params):
        """ update data with keywords paramaters.
        
        params is dictionary.
        use this method, like a update() of dictionary type.

        >>> D = {1: 2}
        >>> D.update(foo="bar")
        >>> D
        {1: 2, "foo": "bar"}
        """

## models
class IWidget(Interface):
    template_name = Attribute("""render template name""")
    type = Attribute(""" type """)

class IAsset(Interface):
    type = Attribute(""" type """)

class IHasMedia(Interface):
    """ using media data. e.g. flash, image, .etc
    """
    alt = Attribute(""" alt """)
    size = Attribute("""size """)
    width = Attribute(""" width""")
    height = Attribute(""" height """)
    filepath = Attribute(""" filepath """)
    mimetype = Attribute(""" mimetype """)

class IHasTimeHistory(Interface):
    """ has time history. 
    """
    created_at = Attribute(""" a time at object created""")
    updated_at = Attribute(""" a time at object updated""")
# 
