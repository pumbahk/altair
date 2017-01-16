# -*- coding: utf-8 -*-

import json
import re
from datetime import datetime, date
from collections import Iterable

from altair.app.ticketing.helpers.base import date_time_helper

import logging
logger = logging.getLogger(__name__)

class MacroEngine:
    # 正規表現のparseには限界がある...
    def build(self, template, data, cache_mode=False):
        result = [ ]
        for m in re.finditer(r'(.+?)(?:{{([0-9a-z_]+(?:\.[0-9a-z_]+(\(.*?\))?)*)}}|\Z)', template, re.MULTILINE | re.DOTALL):
            result.append(m.group(1))
            if m.group(2) is not None and 0 < len(m.group(2)):
                if cache_mode:
                    # _macro()を使わず、単にdict参照のみで変換
                    if data and m.group(2) in data:
                        result.append(data[m.group(2)])
                else:
                    r = self._macro(m.group(2), data)
                    if r is None:
                        # 置換失敗時にマクロを残す
                        # これだと、結果がNoneだった場合と区別がつかない
                        result.append("{{%s}}" % m.group(2))
                    else:
                        result.append(r)
        return u"".join(result)

    def fields(self, template):
        result = []
        for m in re.finditer(r'(.+?)(?:{{([0-9a-z_]+(?:\.[0-9a-z_]+(\(.*?\))?)*)}}|\Z)', template, re.MULTILINE | re.DOTALL):
            name = m.group(2)
            if name is not None:
                if name not in result:
                    result.append(name)
        return result

    def _stringify(self, r):
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
        else:
            return r

    def label(self, macro):
        """
            label('a.func().as(LABEL)') -> 'LABEL'
        """
        labeled = self._macro(macro, None, get_as=True)

        return macro if labeled is None else labeled

    # 先頭から1つ処理して、残りについて再帰呼び出し
    def _macro(self, macro, data, to_string=True, get_as=False):
        # データの前処理
        if hasattr(data, '__call__'):
            data = data()

        if macro is None:
            # no more macro
            if to_string:
                # 文字列化して出力したい場合, names is Noneの時に限る
                return self._stringify(data)
            else:
                return data

        # マクロの処理
        if not isinstance(macro, unicode):
            raise Exception("macro should be unicode")

        m = re.match(r"([0-9a-z_]+(?:\(.*?\))?)(?:\.(.+))?", macro)
        if not m:
            # 異常なnameが渡された
            # return "?"
            raise Exception("wrong macro: %s" % macro)
        name = m.group(1)
        names = m.group(2)

        def process_next(data):
            return self._macro(names, data, to_string=to_string, get_as=get_as)

        m = re.match(r"as\(([^\"]+)\)", name)
        if m:
            if get_as:
                return m.group(1)
            else:
                return process_next(data)

        # .format(f) -> str
        m = re.match(r"format\(\"([^\"]+)\"\)", name)
        if m:
            format = m.group(1)
            return process_next(format.format(self._stringify(data)))

        # .join(sep) -> str
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
                        result.append(self._macro(None, e, to_string=True, get_as=get_as))
                return process_next(m.group(1).join(result))
            else:
                # 非配列に対して.join()指定された
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
        m = re.match(r"map\(\.([0-9a-z_]+)\)", name)
        if m:
            subname = m.group(1)
            if isinstance(data, list):
                result = []
                for e in data:
                    result.append(self._macro(subname, e, to_string=False, get_as=get_as))
                return process_next(result)
            else:
                # 非配列に対して.map()指定された
                return process_next(None)

        try:
            if hasattr(data, name):
                return process_next(getattr(data, name))
            elif isinstance(data, Iterable) and name in data:
                return process_next(data[name])
            else:
                # 未知のproperty
                # return "<unknown property: %s in type: %s>" % (name, type(data))
                logger.debug("Unknown property: %s" % name)
                if get_as:
                    return process_next(None)
                else:
                    return ""
        except UnicodeEncodeError as e:
            # 変数名がmultibyteというのは、基本的にはサポートしない
            logger.warn(e.message)
            return ""
