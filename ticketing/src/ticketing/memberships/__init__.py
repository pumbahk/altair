def includeme(config):
    config.add_route("memberships", "/{action}/{membership_id:.*}", )
    config.scan(".views")
    
