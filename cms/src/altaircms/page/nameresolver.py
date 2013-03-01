# -*- coding:utf-8 -*-
from collections import namedtuple
Info = namedtuple("Info", "caption name url title description keywords")
class GetPageInfoException(Exception):
    pass

class OtherPageInfoResolver(object):
    def __init__(self, defaultinfo):
        self.defaultinfo = defaultinfo

    def resolve(self):
        return Info(url=self.resolve_url(), 
                    name=u"", 
                    caption=u"設定された初期設定から", 
                    title=self.resolve_title(), 
                    keywords=self.resolve_keywords(), 
                    description=self.resolve_description())

    def resolve_url(self):
        return self.defaultinfo.url_prefix
    def resolve_title(self):
        return self.defaultinfo.title_prefix
    def resolve_description(self):
        return self.defaultinfo.description
    def resolve_keywords(self):
        return self.defaultinfo.keywords
        

class GenrePageInfoResolver(object):
    skip = 1
    def __init__(self, defaultinfo):
        self.defaultinfo = defaultinfo

    def resolve(self, genre):
        candidates = self.ordered_genres(genre)
        return Info(url=self.resolve_url(genre, candidates=candidates), 
                    caption=u"「%s」のカテゴリトップページとして" % genre.label, 
                    name=genre.label, 
                    title=self.resolve_title(genre, candidates=candidates), 
                    keywords=self.resolve_keywords(genre, candidates=candidates), 
                    description=self.resolve_description(genre))

    def ordered_genres(self, genre):
        if genre is None:
            return []
        gs = list(genre.ancestors)
        gs.insert(0, genre)
        return list(reversed(gs))
        
    ## cached
    def _ordered_genres(self, ordered_genres, genre):
        return ordered_genres or self.ordered_genres(genre)

    def resolve_url(self, genre, candidates=None):
        part = u"/".join([g.name for g in self._ordered_genres(candidates, genre)][self.skip:])
        return u"%s/%s" % ((self.defaultinfo.url_prefix or u"").rstrip("/"), part.lstrip("/"))

    def resolve_title(self, genre, candidates=None):
        part = u"/".join([g.label for g in self._ordered_genres(candidates, genre)][self.skip:])
        return u"%s%s" % ((self.defaultinfo.title_prefix or u"").rstrip("/"), part.lstrip("/"))

    def resolve_description(self, genre):
        return self.defaultinfo.description #genreがdescriptionを持っても良かったかもしれない　

    def resolve_keywords(self, genre, candidates=None):
        genres = [g.label for g in self._ordered_genres(candidates, genre)][self.skip:]
        genres.insert(0, self.defaultinfo.keywords or u"")
        return u", ".join(genres)

class EventPageInfoResolver(object):
    def __init__(self, defaultinfo):
        self.defaultinfo = defaultinfo
        self.genrepage_resolver = GenrePageInfoResolver(defaultinfo)

    def resolve(self, genre, event):
        data = self.genrepage_resolver.resolve(genre)
        return Info(url=self._resolve_url(data.url, event), 
                    caption=u"「%s」のイベント詳細ページとして" % event.title, 
                    name=event.title, 
                    keywords=self._resolve_keywords(data.keywords, event), 
                    title=self._resolve_title(data.title, event), 
                    description=self._resolve_description(data.description, event))
        
    ## cached
    def _resolve_url(self, result, event):
        if not event.code:
            exc = GetPageInfoException("event %s does not has event code." % event.id)
            exc.jmessage = u"イベント:%sにイベントコードが登録されていません" % event.title
            raise exc
        return u"%s/%s" % (result.rstrip("/"), event.code.lstrip("/"))

    def _resolve_title(self, result, event):
        return event.subtitle or event.title

    def _resolve_description(self, result, event):
        return u"%s %s " % (result, event.description)

    def _resolve_keywords(self, result, event):
        r = [event.title]
        for p in event.pagesets:
            for t in p.public_tags:
                if event.organization_id == t.organization_id:
                    r.append(t.label)
        r.append(result)
        return u", ".join(r)

    def resolve_url(self, genre, event):
        return self._resolve_url(self.genrepage_resolver.resolve_url(genre), event)
    def resolve_title(self, genre, event):
        return self._resolve_title(self.genrepage_resolver.resolve_title(genre), event)
    def resolve_description(self, genre, event):
        return self._resolve_description(self.genrepage_resolver.resolve_description(genre), event)
    def resolve_keywords(self, genre, event):
        return self._resolve_keywords(self.genrepage_resolver.resolve_keywords(genre), event)
