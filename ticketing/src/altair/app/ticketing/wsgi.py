from paste.urlmap import URLMap, parse_path_expression
from paste.urlparser import make_static
from pyramid.path import AssetResolver

def direct_static_serving_filter_factory(mappings):
    def direct_static_serving_filter(global_config, app):
        map = URLMap()
        for url_prefix, spec in mappings.items():
            map[parse_path_expression(url_prefix)] = make_static(
                global_config,
                AssetResolver().resolve(spec).abspath(),
                cache_max_age=3600
                )
        map[parse_path_expression('/')] = app
        return map
    return direct_static_serving_filter
