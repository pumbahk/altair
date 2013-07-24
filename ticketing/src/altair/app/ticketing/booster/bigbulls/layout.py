# -*- coding:utf-8 -*-
from markupsafe import Markup
from .reflect import Symbols

class Layout(object):
    symbols = Symbols
    def __init__(self, context, request):
        self.context = context
        self.request = request

    title = u"岩手ビッグブルズ　2013-2014　クラブブルズ会員入会申込ページ"
    mini_title = u"岩手ビッグブルズ　クラブブルズ会員入会申込ページ"
    orderreview_title = u"岩手ビッグブルズ　クラブブルズ会員入会申込ページ"
    complete_title = u"岩手ビッグブルズ　クラブブルズ会員入会申込"
    team_name = u"岩手ビッグブルズ"
    mailaddress = u"bigbulls@tstar.jp"
    contact_name = u"(株)岩手スポーツプロモーション"
    product_name = u"岩手ビッグブルズ 2013-2014 ブースタークラブ"
    tel = u"019-622-6811　(平日 9:30～18:30)"
    ##html
    form_class_name = u"formbigbulls"

    team_index_url= u'http://www.bigbulls.jp/'
    team_index_url_description = u"bigbulls公式ホームページへ"
    index_page_url = u"https://bigbulls.tstar.jp/booster/"
    privacy_url = u"http://ticketstar.jp/privacy"
    mobile_index_page_url = u"http://www.nm.bigbulls.jp/"
    mail_support_message = u"注文受付完了、確認メール等を本登録メールアドレス宛にご案内します。「tstar.jp」からのメールを受信できるよう、お申し込み前にドメイン指定の設定を必ずお願いいたします。"
    dont_include_hyphen_message = u"「－」（ハイフン）を抜いてご入力ください（例：09012341234）"


    t_shirts_mesaage = u"""\
""".replace("\n", "<br/>")



    @property
    def form_html_extra_info(self):
        return Markup(u'<a href="http://bigbulls.jp/blog/2013/06/cb2013-2014club-bulls.html" target=”_blank”><span><small>会員種別についてはこちら</small></span></a>')
    @property
    def mobile_form_html_extra_info(self):
        return Markup(u'<a href="http://www.bigbulls.jp/booster/index.html">※会員種別についてはこちら</a><br/>')

    @property
    def orderreview_url(self):
        return self.request.route_url('order_review.form')

    def static_url(self, name, *args, **kwargs):
        return self.request.static_url("altair.app.ticketing.booster.bigbulls:"+name, *args, **kwargs)

    def relative_path(self, name):
        return "altair.app.ticketing.booster.bigbulls:"+name
