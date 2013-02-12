import os.path

class TagNameResolver(object):
    def __init__(self, request):
        self.request = request

    def _list_from_candidates(self, candidates):
        size = len(candidates)
        return [os.path.join(*candidates[:size-i]) for i in xrange(len(candidates))]

    def list_from_fullname(self, tagname):
        candidates = tagname.split(".")
        self._list_from_candidates(candidates)

    def list_from_genre(self, genre):
        rancestors = [g.name for g in reversed(genre.ancestors)]
        rancestors.append(genre.name)
        return self._list_from_candidates(rancestors)
