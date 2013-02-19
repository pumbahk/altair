#
def includeme(config):
    config.add_panel(".performance.performance_describe_panel", "describe_performance", 
                     renderer="altaircms:templates/performance/_describe.html")

    config.add_panel(".event.event_page_section_panel", "event_pageset", 
                     renderer="altaircms:templates/pagesets/_event_pageset_list.html")
    config.add_panel(".event.event_performance_section_panel", "event_performance", 
                     renderer="altaircms:templates/performance/_performance_tabs.html")
    config.add_panel(".event.event_description_section_panel", "event_description", 
                     renderer="altaircms:templates/event/_description_table.html")

    config.add_panel(".action.model_action_buttons_panel", "model_action_buttons", 
                     renderer="altaircms:templates/action/model_action_buttons.html")

