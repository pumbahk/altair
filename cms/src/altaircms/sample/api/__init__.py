# -*- coding:utf-8 -*-

def includeme(config):
    config.add_route("foo", "/api/blocks/save", request_method="POST")
    config.add_route("sample::structure_create", "/api/structure/create")
    config.add_route("sample::structure_delete", "/api/structure/delete")
    config.add_route("sample::structure", "/api/structure")

    ## api view
    config.add_route("sample::load_stage", "/api/load/stage", request_method="GET")
    config.add_route("sample::load_layout", "/api/load/layout", request_method="GET")
    config.add_route("sample::save_layout", "/api/save/layout", request_method="POST")
    config.add_route("sample::load_block", "/api/load/block", request_method="GET")
    config.add_route("sample::move_block", "/api/move/block", request_method="POST")
    config.add_route("sample::save_block", "/api/save/block", request_method="POST")

    # config.add_route("sample::load_widget", "/api/load/widget", request_method="GET")
    config.add_route("sample::save_widget", "/api/save/widget", request_method="POST")
    config.add_route("sample::delete_widget", "/api/delete/widget", request_method="POST")

