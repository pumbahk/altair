from wtforms.compat import text_type

class Rendrant(text_type):
    context = None

    def bind(self, context):
        self.context = context

    def __html__(self):
        return self

    def __init__(self, field, html):
        self.field = field

    def render_js_data_provider(self, registry_var_name):
        pass

    def __new__(cls, field, html, *args, **kwargs):
        return text_type.__new__(cls, html)


class RenderingContext(object):
    def __init__(self, default_args={}):
        self.default_args = default_args
        self.rendrants = {}
        self.serial = 0

    def render(self, render, **kwargs):
        kwargs = dict(self.default_args, **kwargs)
        retval = render(context=self, **kwargs)
        if isinstance(retval, Rendrant):
            retval.bind(self)
            self.rendrants[retval.field.short_name] = retval
        self.serial += 1
        return retval
