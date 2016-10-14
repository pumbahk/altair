from webhelpers.paginate import PageURL_WebOb
from markupsafe import Markup, escape

class Helpers(object):
    def __init__(self, request):
        self.request = request

    def render_bootstrap_pager(self, page, arrows=True, urlgen=None):
        set = (page.page - 1) / page.items_per_page

        if urlgen is None:
            urlgen = PageURL_WebOb(self.request)
        html = [
            u'<div class="pagination"><ul>',
            ]
        if arrows:
            if page.first_page is not None and page.page > page.first_page:
                disabled_class = u''
                prev_url = urlgen((set - 1) * page.items_per_page + 1)
            else:
                disabled_class = u' class="disabled"'
                prev_url = u'#'
            html.append(
                u'<li%s><a href="%s"><span aria-hidden="true">&laquo;</span></a></li>' % (
                    disabled_class,
                    escape(prev_url)
                    )
                )
        if page.last_page is not None:
            first = set * page.items_per_page + 1
            last = first + page.items_per_page
            if last > page.last_page:
                last = page.last_page
            for i in range(first, last):
                active_class = u' class="active"' if i == page.page else u''
                url = urlgen(i)
                html.append(u'<li%s><a href="%s">%d</a></li>' % (
                    active_class,
                    escape(url),
                    i))

        if arrows:
            if page.last_page is not None and page.page < page.last_page:
                disabled_class = u''
                next_url = urlgen((set + 1) * page.items_per_page + 1)
            else:
                disabled_class = u' class="disabled"'
                next_url = u'#'
            html.append(u'<li%s><a href="%s"><span aria-hidden="true">&raquo;</span></a></li>' % (
                    disabled_class,
                    escape(next_url)
                    )
                )
        html.append(u'</ul></div>')
        return Markup(u''.join(html))
