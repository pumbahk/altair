# -*- coding:utf-8 -*-

import pyramid.testing as testing
import altaircms.front.views as views
def _create_page(page_name):
    from altaircms.page import models as m
    def set_with_dict(obj, D):
        for k, v in D.items():
            setattr(obj, k, v)
        return obj

    page = m.Page()
    params = {'description': u'boo',
              'keyword': u'oo',
              'tags': u'ooo',
              'url': page_name, 
              'layout_id': 1,
              'title': "fofoo", 
              'structure': u'{}'
              }
    page = set_with_dict(page, params)
    m.DBSession.add(page)
    import transaction
    transaction.commit()
    m.DBSession.remove()
    return page

def get_page(page_name):
    from altaircms.page import models as m
    try:
        return m.Page.query.filter(m.Page.url==page_name).one()
    except:
        return None
    
page_name = "sample_page"
request = testing.DummyRequest()
page = get_page(page_name)
if page is None:
    _create_page(page_name)
    page = get_page(page_name)
request.matchdict = {"page_name": page.url}
# print unicode(views.view(request))
print views.view(request)

