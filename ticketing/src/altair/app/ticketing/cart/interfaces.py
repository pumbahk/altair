# -*- coding:utf-8 -*-

""" TBA
"""
#from altair.app.ticketing.mails.interfaces import ICompleteMailDelivery, ICompleteMailPayment
#from altair.app.ticketing.mails.interfaces import IOrderCancelMailDelivery, IOrderCancelMailPayment
from zope.interface import Interface, Attribute

class IPaymentMethodManager(Interface):
    def get_url(payment_method_id):
        """ 決済フォームURL
        """

    def add_url(payment_method_id, url):
        """ 決済フォームURL登録
        """

class ICartDelivery(Interface):
    """ 確認画面の配送ビューレットのコンテキスト"""
    cart = Attribute(u"カート")

class ICartPayment(Interface):
    """ 確認画面の決済ビューレットのコンテキスト"""
    cart = Attribute(u"カート")

class IStocker(Interface):
    def take_stock(performance_id, product_requires):
        """ 在庫取得
        :param product_requires: list of tuple (product_id, quantity)
        :return: list of tuple (StockStatus, quantity)
        """

class IReserving(Interface):
    def reserve_selected_seats(performance_id, product_requires):
        """ 座席指定
        :param: performance_id パフォーマンス
        :param: product_requires 商品と数量のペアのリスト
        :return: list of seat
        """

    def reserve_seats(stock_id, quantity):
        """ お任せ席指定 
        :param stock_id: 在庫
        :param quantity: 数量
        :return: list of seat
        """

class ICartFactory(Interface):
    def create_cart():
        """
        カート作成
        """

class IPerformanceSelector(Interface):
    def __call__():
        """ 絞り込みキーと販売区分のOrderedDict
        """

    def select_value(performance):
        """ 絞り込みキーの値取得
        """

    label = Attribute(u"絞り込みの項目名")
    second_label = Attribute(u"公演決定の項目名")

class IPageFlowPredicate(Interface):
    def __call__(pe, flow_context, context, request):
        '''合致するならTrueを返す'''

class IPageFlowPredicateUnaryOp(IPageFlowPredicate):
    predicate = Attribute('''''')

class IPageFlowAction(Interface):
    predicates = Attribute(u'遷移条件')
    def __call__(flow_context, context, request):
        pass

class ICartResource(Interface):
    event = Attribute("event")
    performance = Attribute("event")
    sales_segment = Attribute("sales_segment")
    raw_sales_segment = Attribute("raw_sales_segment")
    sales_segments = Attribute("sales_segments")
    membership = Attribute("memberships")
    memberships = Attribute("memberships")
    membergroups = Attribute("membergroups")

    available_sales_segments = Attribute("sales_segments")
    available_payment_delivery_method_pairs = Attribute("")

    login_required = Attribute("")

    cart = Attribute("cart")
    read_only_cart = Attribute("cart")

    products_dict = Attribute("")

    host_base_url = Attribute("")

    user_object = Attribute("""ログイン中のUserのオブジェクト""")

    booster_cart = Attribute("")

    cart_setting = Attribute("")

    def get_total_orders_and_quantities_per_user(sales_segment):
        pass

    def check_order_limit():
        pass

    def authenticated_user():
        pass

    def _populate_params():
        """initialize attributes. if invalid None is stored"""

    def get_payment_delivery_method_pair(start_at=None):
        pass

    def store_user_profile(data):
        """after product form validation,  validation is success,  store data"""

    def load_user_profile():
        pass

    def remove_user_profile():
        pass

class ICartSetting(Interface):
    organization = Attribute('')
    name = Attribute('')
    type = Attribute('')
    performance_selector = Attribute('')
    performance_selector_label1_override = Attribute('')
    performance_selector_label2_override = Attribute('')
    default_prefecture = Attribute('')
    flavors = Attribute('')
    title = Attribute('')
    contact_url = Attribute('')
    contact_url_mobile = Attribute('')
    contact_tel = Attribute('')
    contact_office_hours = Attribute('')
    contact_name = Attribute('')
    mobile_marker_color = Attribute('')
    mobile_required_marker_color = Attribute('')
    mobile_header_background_color = Attribute('')
    fc_announce_page_url = Attribute('')
    fc_announce_page_url_mobile = Attribute('')
    fc_announce_page_title = Attribute('')
    privacy_policy_page_url = Attribute('')
    privacy_policy_page_url_mobile = Attribute('')
    legal_notice_page_url = Attribute('')
    legal_notice_page_url_mobile = Attribute('')
    mail_filter_domain_notice_template = Attribute('')
    orderreview_page_url = Attribute('')
    extra_footer_links = Attribute('')
    extra_footer_links_mobile = Attribute('')
    extra_form_fields = Attribute('')

class ICartRequest(object):
    organization = Attribute('')
    altair_auth_info = Attribute('')
