#
def includeme(config):
    config.add_panel(".performance.performance_describe_panel", "describe_performance", 
                     renderer="altaircms:templates/performance/_describe.html")

