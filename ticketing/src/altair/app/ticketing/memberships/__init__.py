def includeme(config):
    config.add_route("memberships", "/memberships/{action}/{membership_id:.*}", )
    config.add_route("membergroups", "/membergroups/{action}/{membergroup_id:.*}", )
    config.add_route("membergroups.sales_segment_groups", "/sales_segment_groups/{action}/{membergroup_id:.*}", )
    config.add_route("membergrups.api.sales_segment_groups.candidates", "/api/{event_id}")
    config.add_route('memberships.visible', '/visible')
    config.add_route('memberships.invisible', '/invisible')
    config.scan(".views")
    
VISIBLE_MEMBERSHIPS_SESSION_KEY = "_visible_memberships"