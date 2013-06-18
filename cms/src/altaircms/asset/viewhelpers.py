from markupsafe import Markup
import altaircms.helpers as h

def image_asset_layout(request, asset, href=None, width="50px", height="50px"):
    if asset is None:
        u""
    else:
        params = dict(href=href or h.asset.rendering_object(request, asset).image_path,
                      width=width, 
                      height=height, 
                      alt=asset.title)
        return Markup(u"""
<a href="%(href)s"><img src="%(href)s" width="%(width)s" height="%(height)s" alt="%(alt)s"/></a>
""" %  params)
