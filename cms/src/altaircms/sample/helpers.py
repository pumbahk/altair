from markupsafe import Markup

def markup(html):
    return MarkUp(html)

def markup_render(form):
    return Markup(form.render())
