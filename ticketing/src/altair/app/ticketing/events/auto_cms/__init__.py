# -*- coding: utf-8 -*-


def setup_static_views(config):
    """
    settings = config.registry.settings
    config.include("altair.cdnpath")
    from altair.cdnpath import S3StaticPathFactory
    config.add_cdn_static_path(S3StaticPathFactory(
        settings["s3.bucket_name"],
        exclude=config.maybe_dotted(settings.get("s3.static.exclude.function")),
        mapping={"altair.app.ticketing.auto_cms:auto_cms/static": "/auto_cms/static/"}))
    """
    config.add_static_view("static", "altair.app.ticketing.auto_cms:static", cache_max_age=3600)


def includeme(config):
    setup_static_views(config)

    from .resources import AutoCmsImageResource
    config.add_route('auto_cms.image.index', '/image/{event_id}', factory=AutoCmsImageResource)
    config.add_route('auto_cms.image.edit', '/image/edit/{performance_id}', factory=AutoCmsImageResource)
    config.add_route('auto_cms.image.all_edit', '/image/all_edit/{event_id}', factory=AutoCmsImageResource)
