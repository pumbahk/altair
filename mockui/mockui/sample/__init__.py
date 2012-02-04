def includeme(config):
    config.add_route("sample::sample", "/sample")

    ## api view
    config.add_route("sample::api_load_stage", "/sample/api/load/stage", request_method="GET")
    config.add_route("sample::api_load_layout", "/sample/api/load/layout", request_method="GET")
    config.add_route("sample::api_save_layout", "/sample/api/save/layout", request_method="POST")
    config.add_route("sample::api_load_block", "/sample/api/load/block", request_method="GET")
    config.add_route("sample::api_move_block", "/sample/api/move/block", request_method="POST")
    config.add_route("sample::api_save_block", "/sample/api/save/block", request_method="POST")
    config.add_route("sample::api_load_widget", "/sample/api/load/widget", request_method="GET")
    config.add_route("sample::api_save_widget", "/sample/api/save/widget", request_method="POST")
    config.add_route("sample::api_delete_widget", "/sample/api/delete/widget", request_method="POST")

    ## widget view
    # config.add_route("sample::image_widget", "/widget/image")
    # config.add_route("sample::dummy_widget", "/widget/dummy")
    
