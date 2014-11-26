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
        return dict(
            form=CartSettingForm()
            )

    @view_config(
        route_name='cart_setting.new',
        request_method='POST',
        permission='event_editor'
        )
    def post(self):
        form = CartSettingForm(formdata=self.request.POST)
        if not form.validate():
            return dict(
                form=form
                )
        self.request.session.flash(_(u'設定を登録しました'))
        return HTTPFound(self.request.current_route_path())

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
            form=CartSettingForm(obj=self.context.cart_setting)
            )

    @view_config(
        route_name='cart_setting.edit',
        request_method='POST',
        permission='event_editor'
        )
    def post(self):
        form = CartSettingForm(formdata=self.request.POST)
        if not form.validate():
            return dict(
                form=form
                )
        cart_setting = self.context.cart_setting
        cart_setting.name = form.data['name']
        cart_setting.type = form.data['type']
        cart_setting.performance_selector = form.data['performance_selector']
        cart_setting.performance_selector_label1_override = form.data['performance_selector_label1_override']
        cart_setting.performance_selector_label2_override = form.data['performance_selector_label2_override']
        cart_setting.default_prefecture = form.data['default_prefecture']
        cart_setting.flavors = form.data['flavors']
        cart_setting.title = form.data['title']
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
        cart_setting.header_image_url = form.data['header_image_url']
        cart_setting.header_image_url_mobile = form.data['header_image_url_mobile']
        # cart_setting.extra_footer_links = form.data['extra_footer_links']
        # cart_setting.extra_footer_links_mobile = form.data['extra_footer_links_mobile']
        cart_setting.extra_form_fields = form.data['extra_form_fields']
        self.request.session.flash(_(u'設定を編集しました'))
        import transaction
        transaction.commit()
        return HTTPFound(self.request.current_route_path())