# coding: utf-8
import unicodedata


def get_mobile_route_path(request, pcurl):
    urls = dict({
        'faq':request.route_path('help'),
        'change':request.route_path('information'),
    })
    ret = None
    if pcurl in urls:
        ret = urls[pcurl]
    return ret


def get_smartphone_route_path(request, pcurl):
    urls = dict({
        'faq': request.route_path('smartphone.page', kind='help'),
        'purchase': request.route_path('smartphone.page', kind='purchase'),
        'change': request.route_path('smartphone.page', kind='canceled'),
        'smartphone/inquiry': request.route_path('smartphone.page', kind='inquiry'),
        'privacy': "http://privacy.rakuten.co.jp/",
        'legal': request.route_path('smartphone.page', kind='legal'),
        })
    ret = None
    if pcurl in urls:
        ret = urls[pcurl]
    return ret

def check_pc_page(url):
    urls = []
    urls.append("howto")
    urls.append("terms")
    urls.append("sitemap")
    return url in urls


def trim_japanese(target_str):
    for num, ch in enumerate(target_str):
        try:
            name = unicodedata.name(unicode(ch))
            if name.count("HIRAGANA") or \
               name.count("KATAKANA") or \
               name.count("CJK") or \
               name.count("IDEOGRAPHIC SPACE") or \
               name.count("LEFT BLACK LENTICULAR BRACKET") or \
               name.count("LEFT PARENTHESIS") or \
               name.count("LEFT SQUARE BRACKET"):
                return target_str[0:num]
        except (UnicodeDecodeError, TypeError):
            return target_str[0:num]
    return target_str
