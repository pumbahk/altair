# -*- coding:utf-8 -*-
from markupsafe import Markup

class Layout(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    title = u"入会受付"
    mini_title = u"バンビシャス奈良 ブースタークラブ クラブバンビシャス入会申込ページ"
    orderreview_title = u"バンビシャス奈良 ブースタークラブ クラブバンビシャス申込受付確認ページ"
    complete_title = u"バンビシャス奈良 ブースタークラブ クラブバンビシャス入会申込"
    team_name = u"バンビシャス奈良"
    mailaddress = u"club-bambitious@bambitious.jp"
    contact_name = u"クラブバンビシャス事務局"
    product_name = u"バンビシャス奈良 ブースタークラブ クラブバンビシャス入会申込"
    tel = u"0742-20-1800　(平日：10:00～17:00)"
    ##html
    form_class_name = u"formbambitious"

    team_index_url= u'http://bambitious.jp/'
    team_index_url_description = u"バンビシャス奈良 公式ホームページへ"
    index_page_url = u"http://bambitious.tstar.jp/"
    privacy_url = u"http://www.ticketstar.jp/privacy/"
    mobile_index_page_url = u"bambitious.tstar.jp/"
    mail_support_message = u"注文受付完了、確認メール等を本登録メールアドレス宛にご案内します。「bambitious.jp」からのメールを受信できるよう、お申し込み前にドメイン指定の設定を必ずお願いいたします。"
    dont_include_hyphen_message = u"「－」（ハイフン）を抜いてご入力ください（例：09012341234）"
    t_shirts_mesaage = u"ゴールド会員を選択の方はブースターシャツサイズをお選びください。"

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
        return self.request.static_url("altair.app.ticketing.booster.bambitious:"+name, *args, **kwargs)
    
    def relative_path(self, name):
        return "altair.app.ticketing.booster.bambitious:"+name
