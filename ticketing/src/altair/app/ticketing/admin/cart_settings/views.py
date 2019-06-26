# encoding: utf-8

from pyramid.view import view_defaults, view_config
from pyramid.i18n import TranslationString as _
from pyramid.httpexceptions import HTTPFound
from sqlalchemy.sql.expression import func as sqlfunc
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.views import BaseView
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.core.models import Event, EventSetting, SalesSegmentGroup, SalesSegment
from altair.app.ticketing.cart.models import CartSetting
from altair.app.ticketing.security import get_plugin_names

from . import cart_setting_types
from . import CART_SETTING_TYPE_STANDARD
from .forms import CartSettingForm
from .resources import CartSettingResource
from altair.app.ticketing.events import VISIBLE_CART_SETTING_SESSION_KEY
from datetime import datetime

cart_setting_types_dict = dict(cart_setting_types)

def populate_cart_setting_with_form_data(cart_setting, form):
    cart_setting.name = form.data['name']
    if form.data['type'] is not None:
        cart_setting.type = form.data['type']
    cart_setting.auth_type = form.data['auth_type']
    cart_setting.display_order = form.data['display_order']
    cart_setting.visible = form.data['visible']
    cart_setting.oauth_service_provider = form.data['oauth_service_provider']
    cart_setting.secondary_auth_type = form.data['secondary_auth_type']
    cart_setting.ticketing_auth_key = form.data['ticketing_auth_key']
    cart_setting.performance_selector = form.data['performance_selector']
    cart_setting.performance_selector_label1_override = form.data['performance_selector_label1_override']
    cart_setting.performance_selector_label2_override = form.data['performance_selector_label2_override']
    cart_setting.default_prefecture = form.data['default_prefecture']
    cart_setting.flavors = form.data['flavors']
    cart_setting.title = form.data['title']
    cart_setting.fc_kind_title = form.data['fc_kind_title']
    cart_setting.fc_name = form.data['fc_name']
    cart_setting.lots_date_title = form.data['lots_date_title']
    cart_setting.contact_url = form.data['contact_url']
    cart_setting.contact_url_mobile = form.data['contact_url_mobile']
    cart_setting.contact_tel = form.data['contact_tel']
    cart_setting.contact_office_hours = form.data['contact_office_hours']
    cart_setting.contact_name = form.data['contact_name']
    cart_setting.mobile_marker_color = form.data['mobile_marker_color']
    cart_setting.mobile_required_marker_color = form.data['mobile_required_marker_color']
    cart_setting.mobile_header_background_color = form.data['mobile_header_background_color']
    cart_setting.privacy_policy_page_url = form.data['privacy_policy_page_url']
    cart_setting.privacy_policy_page_url_mobile = form.data['privacy_policy_page_url_mobile']
    cart_setting.legal_notice_page_url = form.data['legal_notice_page_url']
    cart_setting.legal_notice_page_url_mobile = form.data['legal_notice_page_url_mobile']
    cart_setting.mail_filter_domain_notice_template = form.data['mail_filter_domain_notice_template']
    cart_setting.orderreview_page_url = form.data['orderreview_page_url']
    cart_setting.lots_orderreview_page_url = form.data['lots_orderreview_page_url']
    cart_setting.header_image_url = form.data['header_image_url']
    cart_setting.header_image_url_mobile = form.data['header_image_url_mobile']
    # cart_setting.extra_footer_links = form.data['extra_footer_links']
    # cart_setting.extra_footer_links_mobile = form.data['extra_footer_links_mobile']
    cart_setting.extra_form_fields = form.data['extra_form_fields']
    cart_setting.hidden_venue_html = form.data['hidden_venue_html']
    cart_setting.embedded_html_complete_page = form.data['embedded_html_complete_page']
    cart_setting.embedded_html_complete_page_mobile = form.data['embedded_html_complete_page_mobile']
    cart_setting.embedded_html_complete_page_smartphone = form.data['embedded_html_complete_page_smartphone']
    cart_setting.oauth_client_id = form.data['oauth_client_id']
    cart_setting.oauth_client_secret = form.data['oauth_client_secret']
    cart_setting.oauth_endpoint_authz = form.data['oauth_endpoint_authz']
    cart_setting.oauth_endpoint_token = form.data['oauth_endpoint_token']
    cart_setting.oauth_endpoint_token_revocation = form.data['oauth_endpoint_token_revocation']
    cart_setting.oauth_endpoint_api = form.data['oauth_endpoint_api']
    cart_setting.oauth_scope = form.data['oauth_scope']
    cart_setting.openid_prompt = form.data['openid_prompt']
    cart_setting.use_spa_cart = form.data['use_spa_cart'] or False  # Noneとなるケースを考慮し、 'or False'を入れる

class CartSettingViewBase(BaseView):
    def cart_setting_type(self, cart_setting):
        return cart_setting_types_dict.get(cart_setting.type)
    def auth_type_name(self, auth_type):
        auth_type_names_dict = dict(get_plugin_names(self.request))
        return auth_type_names_dict.get(auth_type) if auth_type in auth_type_names_dict else u'なし'

@view_defaults(
    decorator=with_bootstrap,
    renderer='altair.app.ticketing.admin.cart_settings:templates/index.html',
    )
class CartSettingListView(CartSettingViewBase):
    @view_config(route_name='cart_setting.visible', permission='event_editor')
    def visible(self):
        self.request.session[VISIBLE_CART_SETTING_SESSION_KEY] = str(datetime.now())
        return HTTPFound(self.request.route_path("cart_setting.index"))

    @view_config(route_name='cart_setting.invisible', permission='event_editor')
    def invisible(self):
        self.request.session.pop(VISIBLE_CART_SETTING_SESSION_KEY, None)
        return HTTPFound(self.request.route_path("cart_setting.index"))

    @view_config(
        route_name='cart_setting.index',
        permission='event_editor'
        )
    def index(self):
        def make_dict(cart_setting):
            q = DBSession.query(Event) \
                .join(Event.setting) \
                .outerjoin(Event.sales_segment_groups) \
                .outerjoin(SalesSegmentGroup.sales_segments) \
                .filter(EventSetting.cart_setting_id == cart_setting.id)
            return dict(
                cart_setting=cart_setting,
                relevant_events=q.distinct(Event.id).order_by(SalesSegment.start_at).limit(10).all(),
                relevant_events_count=q.from_self(sqlfunc.count(sqlfunc.distinct(Event.id))).scalar()
                )

        cart_settings = self.context.cart_settings
        if not self.request.session.get(VISIBLE_CART_SETTING_SESSION_KEY, None):
            cart_settings = cart_settings.filter(CartSetting.visible == True)
        return dict(
            items=[
                make_dict(cart_setting)
                for cart_setting in cart_settings
                ]
            )

@view_defaults(
    decorator=with_bootstrap,
    renderer='altair.app.ticketing.admin.cart_settings:templates/new.html'
    )
class NewCartSettingView(CartSettingViewBase):
    @view_config(
        route_name='cart_setting.new',
        request_method='GET',
        permission='event_editor'
        )
    def get(self):
        cart_setting_id = self.request.params.get('cart_setting_id')
        try:
            cart_setting_id = long(cart_setting_id)
        except (TypeError, ValueError):
            cart_setting_id = None
        original_cart_setting = None
        if cart_setting_id is not None:
            original_cart_setting = DBSession.query(CartSetting) \
                .filter_by(organization_id=self.context.organization.id, id=cart_setting_id) \
                .first()
        if original_cart_setting is None:
            original_cart_setting = self.context.organization.setting.cart_setting
                
        form = CartSettingForm(obj=original_cart_setting, context=self.context)
        form.name.data = u''
        return dict(form=form)

    @view_config(
        route_name='cart_setting.new',
        request_method='POST',
        permission='event_editor'
        )
    def post(self):
        form = CartSettingForm(formdata=self.request.POST, context=self.context)
        if not form.validate():
            return dict(
                form=form
                )
        cart_setting = CartSetting(organization_id=self.context.organization.id)
        populate_cart_setting_with_form_data(cart_setting, form)
        DBSession.add(cart_setting)
        self.request.session.flash(_(u'設定を登録しました'))
        return HTTPFound(self.request.route_path('cart_setting.index'))

@view_defaults(
    decorator=with_bootstrap,
    renderer='altair.app.ticketing.admin.cart_settings:templates/edit.html'
    )
class EditCartSettingListView(CartSettingViewBase):
    @view_config(
        route_name='cart_setting.edit',
        request_method='GET',
        permission='event_editor'
        )
    def get(self):
        return dict(
            form=CartSettingForm(obj=self.context.cart_setting, context=self.context)
            )

    @view_config(
        route_name='cart_setting.edit',
        request_method='POST',
        permission='event_editor'
        )
    def post(self):
        form = CartSettingForm(formdata=self.request.POST, context=self.context)
        if not form.validate():
            return dict(
                form=form
                )
        cart_setting = self.context.cart_setting
        if not self.request.context.organization.setting.enable_spa_cart \
                and form.data['type'] == CART_SETTING_TYPE_STANDARD:
            # Orgのenable_spa_cartがOFFで、変更後もカートタイプが標準の場合、use_spa_cart設定値は更新しない
            # Orgのenable_spa_cartがON -> OFFに切り替えて、もともとuse_spa_cartがONのカート設定を編集しても
            # 設定を引き継ぐようにする。Orgのenable_spa_cartがON -> OFFに変えるのは、なんらかの理由で一時的に設定を
            # 解除するケースが想定され、Org設定を元に戻しても特に運用側が意識せずに新カートを使えるようにするため。
            # ただし、カートタイプが標準以外に変更された場合は強制OFF(新カートは標準カートのみの機能であるため)
            form.use_spa_cart.data = cart_setting.use_spa_cart
        populate_cart_setting_with_form_data(cart_setting, form)
        self.request.session.flash(_(u'設定を編集しました'))
        import transaction
        transaction.commit()
        return HTTPFound(self.request.current_route_path())
