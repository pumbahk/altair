def includeme(config):
    config.add_route("memberships", "/memberships/{action}/{membership_id:.*}", )
    config.add_route("membergroups", "/membergroups/{action}/{membergroup_id:.*}", )
    config.scan(".views")
    
