# coding: utf-8
from pyramid.renderers import render

def render_widget(widget):
    try:
        templeate_file = 'altaircms:templates/front/widget/%s.mako' % (widget.type)
        result = render(templeate_file, {
            'widget': widget
        })
    except:
        raise

    return result


from altaircms.auth.views import *
from altaircms.event.views import *
from altaircms.base.views import *
from altaircms.page.views import *
from altaircms.front.views import *
from altaircms.asset.views import *
from altaircms.widget.views import *
from altaircms.layout.views import *