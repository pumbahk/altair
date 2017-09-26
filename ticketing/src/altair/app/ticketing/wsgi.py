from paste.urlmap import URLMap, parse_path_expression
from paste.urlparser import StaticURLParser
from pyramid.path import AssetResolver

import re
import os
from paste import fileapp


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


def make_static(global_conf, document_root, cache_max_age=None):
    if cache_max_age is not None:
        cache_max_age = int(cache_max_age)
    return CompressStaticURLParser(
        document_root, cache_max_age=cache_max_age)


class CompressStaticURLParser(StaticURLParser):
    def make_app(self, filename):
        gz_file = "%s.gz" % filename
        if os.path.exists(gz_file):
            # found both original file and .gz file
            return CompressFileApp(filename)
        else:
            return fileapp.FileApp(filename)


class CompressFileApp(fileapp.FileApp):
    def get(self, environ, start_response):
        accept_encodings = re.split(',\s*', environ.get('HTTP_ACCEPT_ENCODING', ''))
        if 'gzip' in accept_encodings:
            # create instance by each request, should cache...
            compress_app = fileapp.FileApp("%s.gz" % self.filename)
            if self.expires:
                compress_app.expires = self.expires
            return compress_app.get(environ, start_response)

        return super(CompressFileApp, self).get(environ, start_response)
