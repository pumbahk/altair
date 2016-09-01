# -*- coding: utf-8 -*-

import json
import re
from datetime import datetime, date
from collections import Iterable

from altair.app.ticketing.helpers.base import date_time_helper


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
                        result.append(unicode(data[m.group(2)]))
                else:
                    r = self._macro(m.group(2), data)
                    if r is None:
                        # 置換失敗時にマクロを残す
                        # これだと、結果がNoneだった場合と区別がつかない
                        result.append("{{%s}}" % m.group(2))
                    else:
                        result.append(unicode(r))
        return "".join(result)

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

    # 先頭から1つ処理して、残りについて再帰呼び出し
    def _macro(self, macro, data, to_string=True):
        # データの前処理
        if hasattr(data, '__call__'):
            data = data()

        # マクロの処理
        if macro is not None:
            macro = unicode(macro)
            m = re.match(r"([0-9a-z_]+(?:\(.*?\))?)(?:\.(.+))?", macro)
            if not m:
                # 異常なnameが渡された
                # return "?"
                raise Exception("wrong macro: %s" % macro)
            name = m.group(1)
            names = m.group(2)

            # .format(f) -> str
            m = re.match(r"format\(\"([^\"]+)\"\)", name)
            if m:
                format = m.group(1)
                return self._macro(names, format.format(self._stringify(data)), to_string=to_string)

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
                            result.append(self._macro(None, e, to_string=True))
                    return self._macro(names, m.group(1).join(result), to_string=to_string)
                else:
                    # 非配列に対して.join()指定された
                    return

            # .unique() -> cont
            # ソートされていなくても良い
            if name == "unique()":
                if isinstance(data, list):
                    result = [ ]
                    for e in data:
                        if e not in result:
                            result.append(e)
                    return self._macro(names, result, to_string=to_string)
                else:
                    # 非配列に対して.unique()指定された
                    return

            # .map(.name) -> cont
            m = re.match(r"map\(\.([0-9a-z_]+)\)", name)
            if m:
                subname = m.group(1)
                if isinstance(data, list):
                    result = []
                    for e in data:
                        result.append(self._macro(subname, e, to_string=False))
                    return self._macro(names, result, to_string=to_string)
                else:
                    # 非配列に対して.map()指定された
                    return

            # method形式じゃなくてpropertyの場合
            if hasattr(data, name):
                r = getattr(data, name)
            elif isinstance(data, Iterable) and name in data:
                r = data[name]
            else:
                # 未知のproperty
                # return "<unknown property: %s in type: %s>" % (name, type(data))
                return ""
            return self._macro(names, r, to_string=to_string)
        elif to_string:
            # 文字列化して出力したい場合, names is Noneの時に限る
            return self._stringify(data)
        else:
            return data
