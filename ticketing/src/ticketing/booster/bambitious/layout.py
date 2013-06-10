# -*- coding:utf-8 -*-
from pyramid.decorator import reify

class Layout(object):
    def __init__(self, request):
        self.request = request

    title = u"バンビシャス奈良 ブースタークラブ入会申込ページ"
    teamname = u"バンビシャス奈良"

    @property
    def orderreview_url(self):
        return self.request.route_url('order_review.form')

    @property
    def style_css(self):
        return self.request.static_url('ticketing.booster.bambitious:static/style.css')

    @property
    def jquery_js(self):
        return self.request.static_url('ticketing.booster.bambitious:static/js/jquery.js')

    @property
    def header_image(self):
        return self.request.static_url('ticketing.booster.bambitious:static/images/head_title.png')

    
