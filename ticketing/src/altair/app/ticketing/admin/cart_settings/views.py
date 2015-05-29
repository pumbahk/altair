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

from . import cart_setting_types
from .forms import CartSettingForm
from .resources import CartSettingResource

cart_setting_types_dict = dict(cart_setting_types)

def populate_cart_setting_with_form_data(cart_setting, form):
    cart_setting.name = form.data['name']
    if form.data['type'] is not None:
        cart_setting.type = form.data['type']
    cart_setting.auth_type = form.data['auth_type']
    cart_setting.secondary_auth_type = form.data['secondary_auth_type']
    cart_setting.nogizaka46_auth_key = form.data['nogizaka46_auth_key']
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

class CartSettingViewBase(BaseView):
    def cart_setting_type(self, cart_setting):
        return cart_setting_types_dict.get(cart_setting.type)

@view_defaults(
    decorator=with_bootstrap,
    renderer='altair.app.ticketing.admin.cart_settings:templates/index.html',
    )
class CartSettingListView(CartSettingViewBase):
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
        return dict(
            items=[
                make_dict(cart_setting)
                for cart_setting in self.context.cart_settings
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
        populate_cart_setting_with_form_data(cart_setting, form)
        self.request.session.flash(_(u'設定を編集しました'))
        import transaction
        transaction.commit()
        return HTTPFound(self.request.current_route_path())
