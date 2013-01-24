# coding: utf-8
from pyramid.path import AssetResolver

def _make_layout_filesession(assetspec):
    from ..filelib import FileSession
    savepath = AssetResolver().resolve(assetspec).abspath()
    filesession = FileSession(make_path=lambda : savepath)
    filesession.assetspec = assetspec
    return filesession

SESSION_NAME = "layout"

def includeme(config):
    """
    altaircms.layout_directory = altaircms:templates/front/layout
    """
    settings = config.registry.settings
    filesession = _make_layout_filesession(settings["altaircms.layout_directory"])
    config.add_filesession(filesession, name=SESSION_NAME)

    config.add_route('layout_demo', '/demo/layout/')
    config.add_route("layout_preview", "/layout/{layout_id}/preview")
    config.add_route("layout_download", '/layout/{layout_id}/download')
    config.add_route("layout_create", "/layout/create/{action}")
    config.add_route("layout_update", "/layout/{id}/update/{action}")
    config.scan(".views")
