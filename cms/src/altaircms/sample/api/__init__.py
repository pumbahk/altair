# -*- coding:utf-8 -*-
from altaircms.sample.api.resources import SampleResource

def includeme(config):
    config.add_route("sample::structure_create", "/api/structure/create")
    config.add_route("sample::structure_update", "/api/structure/update")
    config.add_route("sample::structure_get", "/api/structure/get")
    config.add_route("sample::image_widget_create", "/api/widget/image_widget/create", factory=SampleResource)
    config.add_route("sample::image_widget_update", "/api/widget/image_widget/update", factory=SampleResource)
    config.add_route("sample::image_widget_delete", "/api/widget/image_widget/delete", factory=SampleResource)
    config.add_route("sample::image_widget", "/api/widget/image_widget", factory=SampleResource)

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

