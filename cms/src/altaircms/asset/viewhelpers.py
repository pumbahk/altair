from markupsafe import Markup
import altaircms.helpers as h

def image_asset_layout(request, asset, filepath=None, width="50px", height="50px"):
    if asset is None:
        u""
    else:
        params = dict(href=h.asset.to_show_page(request, asset, filepath=filepath),
                      width=width, 
                      height=height, 
                      alt=asset.title)
        return Markup(u"""
<a href="%(href)s"><img src="%(href)s" width="%(width)s" height="%(height)s" alt="%(alt)s"/></a>
""" %  params)
