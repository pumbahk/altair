from altaircms.modellib import DBSession

def get_ancestors(me, include_self=False):
    """ return ancestors (order: parent, grand parent, ...)
    """
    r = []
    while me.parent:
        r.append(me)
        me = me.parent
    r.append(me)

    ## not include self iff include_self is false
    if not include_self:
        r.pop(0)
    return r

class HasAncestorMixin(object):
    @property
    def ancestors(self):
        return get_ancestors(self, include_self=False)

class GetPagesetAncestor(object):
    def __init__(self, pageset):
        self.pageset = pageset

    def get_ancestors(self, include_self=False):
        return get_ancestors(self.pageset, include_self=include_self)

class GetWithGenrePagesetAncestor(object):
    def __init__(self, pageset):
        self.pageset = pageset

    def get_ancestors(self, include_self=False):
        from altaircms.page.models import PageSet
        from altaircms.models import Genre
        r = get_ancestors(self.pageset, include_self=True)
        parent_pageset = r[-1]
        if not include_self:
            r.pop(0)

        if parent_pageset.genre_id is None:
            return r
        genres = parent_pageset.genre.ancestors_include_self
        qs = DBSession.query(Genre.id, PageSet)
        organization_id = self.pageset.organization_id
        qs = qs.filter(PageSet.organization_id==organization_id, Genre.organization_id==organization_id, PageSet.event_id==None)
        qs = qs.filter(Genre.category_top_pageset_id==PageSet.id, Genre.id.in_(g.id for g in genres))

        D = {g_id:p for g_id, p in qs.all()}
        for g in genres:
            page = D.get(g.id)
            if page:
                r.append(page)
        return r


