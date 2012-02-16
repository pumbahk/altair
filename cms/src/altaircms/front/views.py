# coding: utf-8
from pyramid.renderers import render_to_response
from pyramid.view import view_config

@view_config(route_name="front")
def rendering_page(context, request):
    url = request.matchdict["page_name"]
    page, layout = context.get_page_and_layout(url)
    render_tree = context.get_render_tree(page)
    config = context.get_render_config()
    tmpl = context.get_layout_template(layout, config)
    return render_to_response(
        tmpl, dict(
            page=page,
            display_blocks=render_tree.concrete(config=config)
        ),
        request
    )

