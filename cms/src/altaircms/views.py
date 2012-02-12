# coding: utf-8
from pyramid.renderers import render

def render_widget(request, widget):
    try:
        templeate_file = 'altaircms:templates/front/widget/%s.mako' % (widget.type)
        result = render(templeate_file, {
                    'widget': widget
                    },
                    request=request
                )
    except:
        raise

    return result
