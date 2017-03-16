# -*- coding: utf-8 -*-

import json
import re
from datetime import datetime, date
from collections import Iterable

from altair.app.ticketing.helpers.base import date_time_helper

import cgi
import urlparse

import logging
logger = logging.getLogger(__name__)


class MacroEngine:
    # 正規表現のparseには限界がある...
    def build(self, template, data, cache_mode=False, filters=[]):
        result = [ ]
        for m in re.finditer(r'(.+?)(?:{{([0-9a-z_]+(?:\.[0-9a-z_]+(\(.*?\))?)*)}}|\Z)', template, re.MULTILINE | re.DOTALL | re.IGNORECASE):
            result.append(m.group(1))
            if m.group(2) is not None and 0 < len(m.group(2)):
                selected_filters = self._macro(m.group(2), [ ], get_attr='filter')
                if len(selected_filters) == 0:
                    selected_filters = filters

                if cache_mode:
                    # _macro()を使わず、単にdict参照のみで変換

                    if data and m.group(2) in data:
                        r = data[m.group(2)]
                        result.append(self.apply_filters(r, selected_filters))
                    else:
                        pass
                else:
                    r = self._macro(m.group(2), data)
                    if r is None:
                        # 置換失敗時にマクロを残す
                        # これだと、結果がNoneだった場合と区別がつかない
                        result.append("{{%s}}" % m.group(2))
                    else:
                        # 処理成功
                        result.append(self.apply_filters(r, selected_filters))
        return u"".join(result)

    @staticmethod
    def apply_filters(s, filters=None):
        def make_anchor(text, escape):
            """
                http文字列以外のところは、適切にhtml escapeする
                http文字列のところは、Aタグにする
            """

            blocks = re.split(r'(https?://[\x23-\x26\x2b-\x3b\x3d\x3f-\x7e]+)', text)
            result = [escape(blocks.pop(0))]

            while (2 <= len(blocks)):
                escaped_url = cgi.escape(blocks.pop(0), quote=True)
                result.append('<a href="%s">%s</a>' % (escaped_url, escaped_url))
                result.append(escape(blocks.pop(0)))
            return ''.join(result)

        for f in filters:
            if f == 'link':
                s = make_anchor(s, escape=cgi.escape).replace("\n", "<br />\n")
            elif f == 'html':
                s = cgi.escape(s).replace("\n", "<br />\n")
            else:
                # param[x=y&z=] -> str
                m = re.match(r"param\[([^\"]+)\]", f)
                if m:
                    replace = urlparse.parse_qs(m.group(1), keep_blank_values=True).keys()
                    parsed = urlparse.urlsplit(s, allow_fragments=False)
                    params = [p for p in urlparse.parse_qsl(parsed.query, keep_blank_values=True) if
                              p[0] not in replace]
                    query = "&".join(["=".join(p) for p in params] + [m.group(1)])
                    s = urlparse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, query, parsed.fragment))

        return s

    @staticmethod
    def fields(template):
        result = []
        for m in re.finditer(r'(.+?)(?:{{([0-9a-z_]+(?:\.[0-9a-z_]+(\(.*?\))?)*)}}|\Z)', template, re.MULTILINE | re.DOTALL | re.IGNORECASE):
            name = m.group(2)
            if name is not None:
                if name not in result:
                    result.append(name)
        return result

    @staticmethod
    def _stringify(r):
        if isinstance(r, datetime):
            r = date_time_helper.datetime(r)
        if isinstance(r, date):
            r = date_time_helper.date(r)
        if isinstance(r, str) or isinstance(r, unicode):
            return r
        elif isinstance(r, list):
            def dump_obj(o):
                return {"__repr__": repr(o)}
                # raise TypeError(repr(o) + " is not JSON serializable")

            return json.dumps(r, default=dump_obj)
        elif r is None:
            return ""
        else:
            return r

    def label(self, macro):
        """
            label('a.func().as(LABEL)') -> 'LABEL'
            label('a') -> a
        """
        return self._macro(macro, None, get_attr='as')

    # 先頭から1つ処理して、残りについて再帰呼び出し
    def _macro(self, macro, data, to_string=True, get_attr=None):
        logger.debug("macro=%s", macro)

        # データの前処理
        if hasattr(data, '__call__'):
            data = data()

        if macro is None:
            # no more macro
            if get_attr is not None:
                return data
            elif to_string:
                # 文字列化して出力したい場合, names is Noneの時に限る
                return self._stringify(data)
            else:
                return data

        # マクロの処理
        if not isinstance(macro, unicode):
            raise Exception("macro should be unicode")

        m = re.match(r"([0-9a-z_]+(?:\(.*?\))?)(?:\.(.+))?", macro, re.DOTALL | re.IGNORECASE)
        if not m:
            # 異常なnameが渡された
            # return "?"
            raise Exception("wrong macro: %s" % macro)
        name = m.group(1)
        names = m.group(2)

        def process_next(data):
            return self._macro(names, data, to_string=to_string, get_attr=get_attr)

        # .as(label)
        m = re.match(r"as\(([^\"]+)\)", name)
        if m:
            if get_attr == 'as':
                return m.group(1) # stop macro processing
            else:
                return process_next(data)

        # .filter(name)
        m = re.match(r"filter\(([^\"]+)\)", name)
        if m:
            if get_attr == 'filter':
                data_copied = data[:]
                data_copied.append(m.group(1)) # add only
                return data_copied # stop macro processing
            else:
                return process_next(data)
        else:
            if get_attr == 'filter':
                return process_next(data)  # use default filter as data param

        # .default("v") -> str
        m = re.match(r"default\(\"([^\"]+)\"\)", name, re.DOTALL)
        if m:
            return process_next(m.group(1) if data is None else data)

        # .format("f") -> str
        m = re.match(r"format\(\"([^\"]+)\"\)", name)
        if m:
            format = m.group(1)
            return process_next(format.format(self._stringify(data)))

        # .join("sep") -> str
        m = re.match(r"join\(\"([^\"]+)\"\)", name)
        if m:
            if isinstance(data, list):
                result = [ ]
                for e in data:
                    if e is None:
                        pass
                    elif e == "":
                        pass
                    else:
                        # FIXME: strにできない可能性あり
                        result.append(self._macro(None, e, to_string=True, get_attr=get_attr))
                return process_next(m.group(1).join(result))
            else:
                # 非配列に対して.join()指定された
                return process_next(None)

        # .element(i) -> cont
        m = re.match(r"element\((\d+)\)", name)
        if m:
            index = int(m.group(1))
            if isinstance(data, list) and index < len(data):
                return process_next(data[index])
            else:
                return process_next(None)

        # .unique() -> cont
        # ソートされていなくても良い
        if name == "unique()":
            if isinstance(data, list):
                result = [ ]
                for e in data:
                    if e not in result:
                        result.append(e)
                return process_next(result)
            else:
                # 非配列に対して.unique()指定された
                return process_next(None)

        # .map(.name) -> cont
        m = re.match(r"map\(\.([0-9a-z_]+)\)", name, re.IGNORECASE)
        if m:
            subname = m.group(1)
            if isinstance(data, list):
                result = []
                for e in data:
                    result.append(self._macro(subname, e, to_string=False, get_attr=get_attr))
                return process_next(result)
            else:
                # 非配列に対して.map()指定された
                return process_next(None)

        try:
            if get_attr == 'as':
                return process_next(name)
            elif hasattr(data, name):
                return process_next(getattr(data, name))
            elif isinstance(data, Iterable) and name in data:
                return process_next(data[name])
            else:
                # 未知のproperty
                # return "<unknown property: %s in type: %s>" % (name, type(data))
                if data is not None:
                    logger.debug("Unknown property: %s" % name)
                return process_next(None)
        except UnicodeEncodeError as e:
            # 変数名がmultibyteというのは、基本的にはサポートしない
            logger.warn(e.message)
            return ""


html_filter = 'html'
