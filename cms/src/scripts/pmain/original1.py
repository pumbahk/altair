"""
create template
"""
def main(app):
    from pyramid.renderers import render
    print render("altaircms:templates/front/original1/base.mako", {})
