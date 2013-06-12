# -*- coding:utf-8 -*-
from markupsafe import Markup

class Layout(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    title = u"バンビシャス奈良 ブースタークラブ クラブバンビシャス入会申込ページ"
    mini_title = u"バンビシャス奈良 ブースタークラブ クラブバンビシャス入会申込ページ"
    orderreview_title = u"バンビシャス奈良 ブースタークラブ クラブバンビシャス入会申込ページ 受付確認ページ"
    complete_title = u""
    team_name = u"バンビシャス奈良"
    mailaddress = u"bambitious@tstar.jp"
    contact_name = u"バンビシャス奈良チケット事務局"
    product_name = u"バンビシャス奈良 ブースタークラブ クラブバンビシャス入会申込"
    tel = u"0742-20-1800　(平日：10:00～17:00)"
    ##html
    form_class_name = u"formbambitious"

    team_index_url= u'http://bambitious.jp/'
    team_index_url_description = u"バンビシャス奈良 公式ホームページへ"
    index_page_url = u"http://bambitious.tstar.jp/"
    mobile_index_page_url = u"bambitious.tstar.jp/"

    @property
    def form_html_extra_info(self):
        return u""
    @property
    def mobile_form_html_extra_info(self):
        return u""

    @property
    def orderreview_url(self):
        return self.request.route_url('order_review.form')

    def static_url(self, name, *args, **kwargs):
        return self.request.static_url("ticketing.booster.bambitious:"+name, *args, **kwargs)
    
    def relative_path(self, name):
        return "ticketing.booster.bambitious:"+name
