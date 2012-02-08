def includeme(config):
    config.add_route("sample::sample", "/sample")
    config.add_route("sample::freetext", "/freetext")

    ## api view
    config.add_route("sample::api_load_stage", "/api/load/stage", request_method="GET")
    config.add_route("sample::api_load_layout", "/api/load/layout", request_method="GET")
    config.add_route("sample::api_save_layout", "/api/save/layout", request_method="POST")
    config.add_route("sample::api_load_block", "/api/load/block", request_method="GET")
    config.add_route("sample::api_move_block", "/api/move/block", request_method="POST")
    config.add_route("sample::api_save_block", "/api/save/block", request_method="POST")
    # config.add_route("sample::api_load_widget", "/api/load/widget", request_method="GET")
    config.add_route("sample::api_save_widget", "/api/save/widget", request_method="POST")
    config.add_route("sample::api_delete_widget", "/api/delete/widget", request_method="POST")

    ## widget view
    config.add_route("sample::image_widget", "/api/load/widget/image")
    config.add_route("sample::freetext_widget", "/api/load/widget/freetext")
    # config.add_route("sample::dummy_widget", "/widget/dummy")
    
