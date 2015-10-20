from pyramid.security import Allow, Deny, Authenticated, DENY_ALL
class BaseResource(object):
    __acl__ = [
        (Allow, Authenticated, 'authenticated'),
        (Allow, 'administrator', 'manage_operators'),
        (Allow, 'administrator', 'manage_oauth_clients'),
        (Allow, 'administrator', 'manage_member_sets'),
        (Allow, 'administrator', 'manage_member_kinds'),
        (Allow, 'administrator', 'manage_members'),
        (Allow, 'operator', 'manage_members'),
        (Allow, 'operator', 'manage_member_kinds'),
        DENY_ALL,
        ]

    def __init__(self, request):
        self.request = request
