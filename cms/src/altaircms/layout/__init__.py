# coding: utf-8
from pyramid.path import AssetResolver

SESSION_NAME = "cms-layout-templates"

def install_filesession(config):
    from ..filelib import FileSession
    settings = config.registry.settings
    assetspec = settings["altaircms.layout_directory"]
    savepath = AssetResolver().resolve(assetspec).abspath()
    filesession = FileSession(make_path=lambda : savepath, 
                              marker=SESSION_NAME, 
                              options={"public": False})
    filesession.assetspec = assetspec
    config.add_filesession(filesession, name=SESSION_NAME)

def install_s3sync(config):
    ## s3 upload setting
    ## after s3 upload event
    ## file upload -> s3 upload -> set uploaded
    config.add_subscriber(".subscribers.rename_for_s3_upload", "altaircms.filelib.s3.BeforeS3Upload")
    config.add_subscriber(".subscribers.set_uploaded_at", "altaircms.filelib.s3.AfterS3Upload")

def includeme(config):
    """
    altaircms.layout_directory = altaircms:templates/front/layout
    """
    config.include(install_filesession)
    config.include(install_s3sync)

    config.add_route('layout_demo', '/demo/layout/')
    config.add_route("layout_preview", "/layout/{layout_id}/preview")
    config.add_route("layout_download", '/layout/{layout_id}/download')
    config.add_route("layout_list", "/layout")
    config.add_route("layout_list_with_pagetype", "/layout/pagetype/{pagetype_id}")
    config.add_route("layout_detail", "/layout/{layout_id}/detail")
    config.add_route("layout_sync", "/layout/{layout_id}/sync")
    config.add_route("layout_create", "/layout/pagetype/{pagetype_id}/create/{action}")
    config.add_route("layout_update", "/layout/{id}/pagetype/{pagetype_id}/update/{action}")
    config.scan(".views")
