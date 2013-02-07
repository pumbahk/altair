# -*- coding:utf-8 -*-
import datetime


class RawText(object):
    def __init__(self, v):
        self.value = v

    def __html__(self):
        return self.value

WEEK =[u"月", u"火", u"水", u"木", u"金", u"土", u"日"]
import urllib
def path_in_string(path, string):
    path = urllib.unquote_plus(path)
    return path.endswith(string)


def countdown_days_from(limit_date, today_fn=datetime.datetime.now):
    today = today_fn()
    if today > limit_date:
        return 0
    else:
        return (limit_date-today).days

def list_to_attibutes(attr_list):
    """
    >>> attr_list = [("id", "foo"), ("class", "bar")]
    >>> list_to_attibutes(attr_list)
    u'id="foo" class="bar"'
    """
    return u" ".join(u'%s="%s"' % (k, v) for k, v in attr_list)
    

def make_link(title, url):
    """
    >>> make_link("foo", "http://example.com")
    u'<a href="http://example.com">foo</a>'
    """
    return u'<a href="%s">%s</a>' % (url, title)

def nl_to_br(string, rawtext=True):
    return RawText(string.replace("\n", "<br/>"))

WEEK =[u"月", u"火", u"水", u"木", u"金", u"土", u"日"]
def jdate(d):
    """ dateオブジェクトを受け取り日本語の日付を返す
    >>> from datetime import date
    >>> jdate(date(2011, 1, 1))
    u'2011\u5e7401\u670801\u65e5'
    """
    if d:
        datestr = d.strftime(u"%Y年%-m月%-d日".encode("utf-8")).decode("utf-8")
        return u"%s（%s）" % (datestr, unicode(WEEK[d.weekday()]))
    else:
        return u"-"

def jdate_with_hour(d):
    if d:
        datestr = d.strftime(u"%Y年%-m月%-d日 %-H:%-M".encode("utf-8")).decode("utf-8")
        return u"%s（%s）" % (datestr, unicode(WEEK[d.weekday()]))
    else:
        return u"-"

def translate_longtext_to_simple_html(string):
    """
    abcdef
    xyz
    => <p>abcdef</p><p>xyz</p>


    abcdef

    xyz
    foo
    => <p>abcdef<br/></p><p>xyz</p><p>foo</p>
    """
    return u"<p>%s</p>" % u"</p><p>".join(string.replace("\n\n", "<br/>").split("\n"))

def hidden_input(name, value, id=None):
    fmt = '<input id="%s" name="%s" type="hidden" value="%s" />'
    return fmt % (id or name,  name, value)
        
def confirm_stage():
    return hidden_input("stage", "confirm")
def execute_stage():
    return hidden_input("stage", "execute")

if __name__ == "__main__":
    import doctest
    doctest.testmod()
