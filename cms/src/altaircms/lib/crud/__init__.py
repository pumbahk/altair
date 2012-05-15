def includeme(config):
    config.include("..flow")
    config.define_flow_direction("crud-create-flow", ["input", "confirm", "create"])
    config.define_flow_direction("crud-update-flow", ["input", "confirm", "update"])
    config.define_flow_direction("crud-delete-flow", ["confirm", "delete"])

    config.add_directive("add_crud", ".directives.add_crud")
