from ..security import get_acl_candidates


class ArtistResource(object):

    @property
    def __acl__(self):
        # need permission
        return get_acl_candidates()

    def __init__(self, request):
        self.request = request
