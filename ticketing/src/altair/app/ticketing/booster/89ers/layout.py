# -*- coding:utf-8 -*-
from markupsafe import Markup

class Layout(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    title = u"仙台89ERS 2013-2014 ブースタークラブ入会申込ページ"
    mini_title = u"仙台89ERS ブースタークラブ入会申込ページ"
    orderreview_title = u"仙台89ERS 2013-2014 ブースタークラブ受付確認ページ"
    complete_title = u"仙台89 ERS 2013-2014 ブースター会員申込"
    team_name = u"仙台89ERS"
    mailaddress = u"89ers@tstar.jp"
    contact_name = u"仙台89ERS　ブースタークラブ事務局"
    product_name = u"仙台89ERS 2013-2014 ブースタークラブ"
    tel = u"022-215-8138　(平日：9:00〜18:00)"
    ##html
    form_class_name = u"form89ers"

    team_index_url= u'http://www.89ers.jp/'
    team_index_url_description = u"89ers公式ホームページへ"
    index_page_url = u"https://89ers.tstar.jp/booster/"
    privacy_url = u"http://ticketstar.jp/privacy"
    mobile_index_page_url = u"http://www.nm.89ers.jp/"
    mail_support_message = u"注文受付完了、確認メール等を本登録メールアドレス宛にご案内します。「tstar.jp」からのメールを受信できるよう、お申し込み前にドメイン指定の設定を必ずお願いいたします。"
    dont_include_hyphen_message = u"「－」（ハイフン）を抜いてご入力ください（例：09012341234）"
    t_shirts_mesaage = u"法人/プラチナ/ゴールド会員を選択の方はTシャツサイズをお選びください。"

    @property
    def form_html_extra_info(self):
        return Markup(u'<a href="http://www.89ers.jp/booster/index.html" target=”_blank”><span><small>会員種別についてはこちら</small></span></a>')
    @property
    def mobile_form_html_extra_info(self):
        return Markup(u'<a href="http://www.mobile89ers.jp/imode/cgi-bin/pgget.dll?pg=/i/booster/club/cont/club_p01_00">※会員種別についてはこちら</a><br/>')

    @property
    def orderreview_url(self):
        return self.request.route_url('order_review.form')

    def static_url(self, name, *args, **kwargs):
        return self.request.static_url("altair.app.ticketing.booster.89ers:"+name, *args, **kwargs)

    def relative_path(self, name):
        return "altair.app.ticketing.booster.89ers:"+name
