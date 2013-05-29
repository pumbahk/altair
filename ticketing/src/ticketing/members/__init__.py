import functools 

def includeme(config):
    add_route = functools.partial(config.add_route, factory=".resources.MembersResource")
    add_route("members.membership.index", "/", )
    add_route("members.index", "/membership/{membership_id}")
    add_route("members.member", "/membership/{membership_id}/member/{action}")
    add_route("members.loginuser", "/memberships/{membership_id}/loginuser/{action}/{loginuser_id}")
    config.scan(".views")
