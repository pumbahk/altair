def install_page_panels(config):
    config.add_panel(".page.page_describe_panel", "describe_page", 
                     renderer="altaircms:templates/page/_describe.html")
    config.add_panel(".page.page_accesskey_section_panel", "page_accesskey", 
                     renderer="altaircms:templates/auth/accesskey/_accesskey_describe.html")

def install_pageset_panels(config):
    config.add_panel(".pageset.nav_pageset_panel", "nav_pageset", 
                     renderer="altaircms:templates/pagesets/_nav_pageset.html")
    config.add_panel(".pageset.pageset_page_listing_panel", "pageset_page", 
                     renderer="altaircms:templates/page/_listing_pageset_page.html")

def install_event_panels(config):
    config.add_panel(".event.event_page_section_panel", "event_pageset", 
                     renderer="altaircms:templates/pagesets/_listing_event_pageset.html")
    config.add_panel(".event.event_performance_section_panel", "event_performance", 
                     renderer="altaircms:templates/performance/_performance_tabs.html")
    config.add_panel(".event.event_description_section_panel", "event_description", 
                     renderer="altaircms:templates/event/_description_table.html")
    config.add_panel(".event.event_accesskey_section_panel", "event_accesskey", 
                     renderer="altaircms:templates/auth/accesskey/_accesskey_describe.html")

def install_performance_panels(config):
    config.add_panel(".performance.performance_describe_panel", "describe_performance", 
                     renderer="altaircms:templates/performance/_describe.html")
    config.add_panel(".performance.performance_salessegment_tabs_panel", "performance_salessegment", 
                     renderer="altaircms:templates/salessegment/_salessegment_tabs.html")


def install_salessegment_panels(config):
    config.add_panel(".salessegment.salessegment_describe_panel", "describe_salessegment", 
                     renderer="altaircms:templates/salessegment/_describe.html")
    config.add_panel(".salessegment.salessegment_ticket_tabs_panel", "salessegment_ticket", 
                     renderer="altaircms:templates/ticket/_ticket_table.html")

def install_product_panels(config):
    config.add_panel(".ticket.ticket_describe_panel", "describe_ticket", 
                     renderer="altaircms:templates/ticket/_describe.html")

def install_action_panels(config):
    config.add_panel(".action.model_action_buttons_panel", "model_action_buttons", 
                     renderer="altaircms:templates/action/model_action_buttons.html")
    config.add_panel(".action.create_only_action_buttons_panel", "model_create_only_buttons", 
                     renderer="altaircms:templates/action/model_create_only_buttons.html")

def includeme(config):
    ## model panels
    config.include(install_event_panels)
    config.include(install_performance_panels)
    config.include(install_salessegment_panels)
    config.include(install_product_panels)
    config.include(install_pageset_panels)
    config.include(install_page_panels)

    ## action panels
    config.include(install_action_panels)

    

