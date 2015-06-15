# -*- coding: utf-8 -*-

import webhelpers.paginate as paginate

from pyramid.view import view_config, view_defaults
from pyramid.renderers import render_to_response
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPForbidden
from pyramid.url import route_path
from altair.app.ticketing.master.models import Prefecture

from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.models import merge_session_with_post, record_to_multidict
from altair.app.ticketing.views import BaseView
from altair.app.ticketing.core.models import Organization, OrganizationSetting, Host, Event, Account, MailTypeChoices, SejTenant
from altair.app.ticketing.cart.models import CartSetting
from altair.app.ticketing.operators.models import Operator, OperatorRole, OperatorAuth
from altair.app.ticketing.users.models import User
from altair.app.ticketing.master.models import BankAccount
from altair.app.ticketing.mails.forms import MailInfoTemplate
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.mails.api import get_mail_utility
from altair.app.ticketing.operators import api as o_api
from .forms import (
    OrganizationForm,
    NewOrganizationForm,
    SejTenantForm,
    OrganizationSettingForm,
    OrganizationSettingSimpleForm,
    HostForm,
    )

import logging
logger = logging.getLogger(__name__)

@view_defaults(decorator=with_bootstrap, permission="administrator")
class Organizations(BaseView):

    @view_config(route_name='organizations.index', renderer='altair.app.ticketing:templates/organizations/index.html')
    def index(self):
        sort = self.request.GET.get('sort', 'Organization.id')
        direction = self.request.GET.get('direction', 'asc')
        if direction not in ['asc', 'desc']:
            direction = 'asc'

        query = Organization.filter()
        query = query.order_by(sort + ' ' + direction)

        organizations = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=20,
            url=paginate.PageURL_WebOb(self.request)
        )

        return {
            'organizations': organizations
        }

    @view_config(route_name='organizations.show', renderer='altair.app.ticketing:templates/organizations/show.html')
    def show(self):
        organization_id = int(self.request.matchdict.get("organization_id", 0))
        organization = Organization.get(organization_id)
        if organization is None:
            return HTTPNotFound("organization id %d is not found" % organization_id)
        sej_tenants = SejTenant.filter_by(organization_id=organization.id).all()
        return {
            'organization':organization,
            'sej_tenants':sej_tenants
        }

    @view_config(route_name='organizations.new', request_method='GET', renderer='altair.app.ticketing:templates/organizations/edit.html')
    def new_get(self):
        return {
            'form': NewOrganizationForm(request=self.request),
            'route_name': u'登録',
            'new_user': True,
            }

    @view_config(route_name='organizations.new', request_method='POST', renderer='altair.app.ticketing:templates/organizations/edit.html')
    def new_post(self):
        f = NewOrganizationForm(self.request.POST, request=self.request)

        if f.validate():
            organization = merge_session_with_post(Organization(), f.data)
            organization.prefecture = Prefecture.get_prefecture_label(f.prefecture_id.data)
            organization.user = User(
                bank_account=BankAccount()
                )
            organization.settings = [
                OrganizationSetting(
                    name='default',
                    performance_selector='matchup',
                    default_mail_sender=f.default_mail_sender.data,
                    cart_setting=CartSetting(
                        organization=organization,
                        name=u'デフォルトの設定',
                        type=u'standard',
                        performance_selector=u'matchup',
                        performance_selector_label1_override=None,
                        performance_selector_label2_override=None,
                        mobile_marker_color=u'#000000',
                        mobile_header_background_color=u'#000000',
                        mobile_required_marker_color=u'#ff0000',
                        mail_filter_domain_notice_template=u'注文受付完了、確認メール等をメールでご案内します。「{domain}」からのメールを受信できるよう、お申し込み前にドメイン指定の設定を必ずお願いいたします。')
                    )
                ]
            organization.operators = [
                Operator(
                    name=f.login.data['name'],
                    email=f.login.data['email'],
                    expire_at=None,
                    status=1,
                    roles=[OperatorRole.query.filter_by(id=1).one()], # XXX
                    auth=OperatorAuth(
                        login_id=f.login.data['login_id'],
                        password=o_api.crypt(f.login.data['password'])
                        )
                    )
                ]
            try:
                organization.save()
            except:
                return {
                    'form': f,
                    'route_name': u'登録',
                    'new_user': True,
                }

            self.request.session.flash(u'配券先／配券元を保存しました')
            return HTTPFound(location=route_path('organizations.show', self.request, organization_id=organization.id))
        else:
            return {
                'form':f,
                'route_name': u'登録',
                'new_user': True,
                }

    @view_config(route_name='organizations.edit', request_method='GET', renderer='altair.app.ticketing:templates/organizations/edit.html')
    def edit_get(self):
        organization_id = int(self.request.matchdict.get('organization_id', 0))
        organization = Organization.get(organization_id)
        if organization is None:
            return HTTPNotFound("organization id %d is not found" % organization_id)

        f = OrganizationForm(organization_id=organization_id)
        f.prefecture_id.default = Prefecture.get_prefecture_id(organization.prefecture)
        f.process(record_to_multidict(organization))
        return {
            'form':f,
            'route_name': u'編集',
            'new_user': False,
            }

    @view_config(route_name='organizations.edit', request_method='POST', renderer='altair.app.ticketing:templates/organizations/edit.html')
    def edit_post(self):
        organization_id = int(self.request.matchdict.get('organization_id', 0))
        organization = Organization.get(organization_id)
        if organization is None:
            return HTTPNotFound("organization id %d is not found" % organization_id)
        f = OrganizationForm(self.request.POST, organization_id=organization_id)
        if f.validate():
            organization = merge_session_with_post(organization, f.data)
            organization.prefecture = Prefecture.get_prefecture_label(f.prefecture_id.data)
            organization.save()

            self.request.session.flash(u'配券先／配券元を保存しました')
            return HTTPFound(location=route_path('organizations.show', self.request, organization_id=organization.id))
        else:
            return {
                'form':f,
                'route_name': u'編集',
                'new_user': False,
                }

    @view_config(route_name='organizations.delete')
    def delete(self):
        organization_id = int(self.request.matchdict.get('organization_id', 0))
        organization = Organization.get(organization_id)
        if organization is None:
            return HTTPNotFound("organization id %d is not found" % organization_id)

        organization.delete()

        self.request.session.flash(u'配券先／配券元を削除しました')
        return HTTPFound(location=route_path('organizations.index', self.request))


@view_defaults(decorator=with_bootstrap, permission="administrator")
class OrganizationSettings(BaseView):
    @view_config(route_name='organizations.settings.edit', request_method='GET', renderer='altair.app.ticketing:templates/organizations/organization_setting/edit.html')
    def edit_get(self):
        organization_id = long(self.request.matchdict.get('organization_id', 0))
        organization = Organization.query.filter_by(id=organization_id).one()
        organization_setting_id = long(self.request.matchdict.get('organization_setting_id', 0))
        organization_setting = OrganizationSetting.query.filter_by(organization_id=organization_id, id=organization_setting_id).first()
        if organization_setting is None:
            return HTTPNotFound("organizationSetting(organization_id=%d, id=%d) is not found" % (organization_setting_id, organization_id))
        f = OrganizationSettingForm(obj=organization_setting, context=self.context)
        return {
            'organization': organization,
            'form':f,
            'route_name': u'編集',
            'route_path': self.request.path,
            }

    @view_config(route_name='organizations.settings.edit', request_method='POST', renderer='altair.app.ticketing:templates/organizations/organization_setting/edit.html')
    def edit_post(self):
        organization_id = long(self.request.matchdict.get('organization_id', 0))
        organization = Organization.query.filter_by(id=organization_id).one()
        organization_setting_id = long(self.request.matchdict.get('organization_setting_id', 0))
        organization_setting = OrganizationSetting.query.filter_by(organization_id=organization_id, id=organization_setting_id).first()
        if organization_setting is None:
            return HTTPNotFound("organizationSetting(organization_id=%d, id=%d) is not found" % (organization_setting_id, organization_id))

        f = OrganizationSettingForm(self.request.POST, obj=organization_setting, context=self.context)
        if not f.validate():
            return {
                'organization': organization,
                'form':f,
                'route_name': u'編集',
                'route_path': self.request.path,
            }

        organization_setting.name = f.name.data
        organization_setting.cart_setting_id = f.cart_setting_id.data
        organization_setting.margin_ratio = f.margin_ratio.data
        organization_setting.refund_ratio = f.refund_ratio.data
        organization_setting.printing_fee = f.printing_fee.data
        organization_setting.registration_fee = f.registration_fee.data
        organization_setting.multicheckout_shop_name = f.multicheckout_shop_name.data
        organization_setting.multicheckout_shop_id = f.multicheckout_shop_id.data
        organization_setting.multicheckout_auth_id = f.multicheckout_auth_id.data
        if f.multicheckout_auth_password.data:
            organization_setting.multicheckout_auth_password = f.multicheckout_auth_password.data
        organization_setting.cart_item_name = f.cart_item_name.data
        organization_setting.contact_pc_url = f.contact_pc_url.data
        organization_setting.contact_mobile_url = f.contact_mobile_url.data
        organization_setting.point_type = f.point_type.data
        organization_setting.point_fixed = f.point_fixed.data
        organization_setting.point_rate = f.point_rate.data
        organization_setting.notify_point_granting_failure = f.notify_point_granting_failure.data
        organization_setting.notify_remind_mail = f.notify_remind_mail.data
        organization_setting.bcc_recipient = f.bcc_recipient.data
        organization_setting.default_mail_sender = f.default_mail_sender.data
        organization_setting.enable_smartphone_cart = f.enable_smartphone_cart.data
        organization_setting.entrust_separate_seats = f.entrust_separate_seats.data
        organization_setting.sales_report_type = f.sales_report_type.data
        organization_setting.sitecatalyst_use = f.sitecatalyst_use.data
        organization_setting.enable_mypage = f.enable_mypage.data
        organization_setting.augus_use = f.augus_use.data
        organization_setting.mail_refund_to_user = f.mail_refund_to_user.data
        organization_setting.asid = f.asid.data
        organization_setting.asid_mobile = f.asid_mobile.data
        organization_setting.asid_smartphone = f.asid_smartphone.data
        organization_setting.lot_asid = f.lot_asid.data
        organization_setting.famiport_enabled = f.famiport_enabled.data
        organization_setting.save()

        self.request.session.flash(u'その他の設定を保存しました')
        return HTTPFound(location=route_path('organizations.show', self.request, organization_id=organization_id))

@view_defaults(decorator=with_bootstrap, permission="organization_editor")
class OrganizationSettingSimples(BaseView):
    @view_config(route_name='organizations.settings.edit.simple', request_method='GET',
                 renderer='altair.app.ticketing:templates/organizations/organization_setting/edit_simple.html')
    def edit_get(self):
        organization_id = self.request.matchdict.get('organization_id', 0)
        organization_setting_id = self.request.matchdict.get('organization_setting_id', 0)

        not_found = HTTPNotFound(
            'OrganizationSetting is not found: Organization.id={} OrganizationSetting.id={}'.format(
                organization_id, organization_setting_id))

        try:
            organization_id = long(organization_id)
            organization_setting_id = long(organization_setting_id)
        except TypeError:
            raise not_found

        if self.request.context.organization:
            organization = Organization.query.filter_by(id=organization_id).first()
            organization_setting = OrganizationSetting\
              .query\
              .filter(OrganizationSetting.organization_id==organization_id)\
              .filter(OrganizationSetting.id==organization_setting_id)\
              .first()
            if self.context.organization \
              and organization and organization_setting\
              and organization.id == self.context.organization.id:
                f = OrganizationSettingSimpleForm(obj=organization_setting, context=self.context)
                return {
                    'organization': organization,
                    'form':f,
                    'route_name': u'編集',
                    'route_path': self.request.path,
                    }
        raise not_found


    @view_config(route_name='organizations.settings.edit.simple', request_method='POST',
                  renderer='altair.app.ticketing:templates/organizations/organization_setting/edit_simple.html')
    def edit_post(self):

        organization_id = self.request.matchdict.get('organization_id', 0)
        organization_setting_id = self.request.matchdict.get('organization_setting_id', 0)

        not_found = HTTPNotFound(
            'OrganizationSetting is not found: Organization.id={} OrganizationSetting.id={}'.format(
                organization_id, organization_setting_id))

        try:
            organization_id = long(organization_id)
            organization_setting_id = long(organization_setting_id)
        except TypeError:
            raise not_found

        if self.request.context.organization:
            organization = Organization.query.filter_by(id=organization_id).first()
            organization_setting = OrganizationSetting\
              .query\
              .filter(OrganizationSetting.organization_id==organization_id)\
              .filter(OrganizationSetting.id==organization_setting_id)\
              .first()
            formdata = self.request.POST
            if self.context.organization \
              and organization and organization_setting\
              and organization.id == self.context.organization.id:
                f = OrganizationSettingSimpleForm(formdata=formdata, context=self.context)
                if not f.validate():
                    return {
                        'organization': organization,
                        'form':f,
                        'route_name': u'編集',
                        'route_path': self.request.path,
                        }
                else:
                    organization_setting.notify_remind_mail = f['notify_remind_mail'].data
                    organization_setting.contact_pc_url = f['contact_pc_url'].data
                    organization_setting.contact_mobile_url = f['contact_mobile_url'].data
                    organization_setting.point_fixed = f['point_fixed'].data
                    organization_setting.point_rate = f['point_rate'].data
                    organization_setting.notify_point_granting_failure = f['notify_point_granting_failure'].data
                    organization_setting.entrust_separate_seats = f['entrust_separate_seats'].data
                    organization_setting.bcc_recipient = f['bcc_recipient'].data
                    organization_setting.default_mail_sender = f['default_mail_sender'].data
                    organization_setting.sales_report_type = f['sales_report_type'].data
                    organization_setting.cart_setting_id = f['cart_setting_id'].data
                    organization_setting.mail_refund_to_user = f['mail_refund_to_user'].data

                    organization_setting.notify_remind_mail = f.notify_remind_mail.data
                    self.request.session.flash(u'その他の設定を保存しました')
                    return HTTPFound(location=route_path(
                        'organizations.settings.edit.simple',
                        self.request, organization_id=organization_id,
                        organization_setting_id=organization_setting_id))
        raise not_found

@view_defaults(decorator=with_bootstrap, permission="administrator")
class SejTenants(BaseView):

    @view_config(route_name='organizations.sej_tenant.new', request_method='GET',
                 renderer='altair.app.ticketing:templates/organizations/sej_tenants/edit.html')
    def new(self):
        organization_id = int(self.request.matchdict.get('organization_id', 0))
        organization = Organization.query.filter_by(id=organization_id).one()
        sej_tenant = SejTenant.query.filter_by(organization_id=organization_id).first()
        if sej_tenant:
            self.request.session.flash(u'既にコンビニ設定があります')
            return HTTPFound(location=route_path('organizations.show', self.request, organization_id=organization_id))

        form = SejTenantForm(organization_id=organization_id)
        return dict(
            form=form,
            organization=organization,
            route_name=u'登録'
            )

    @view_config(route_name='organizations.sej_tenant.new', request_method='POST',
                 renderer='altair.app.ticketing:templates/organizations/sej_tenants/edit.html')
    def new_post(self):
        organization_id = int(self.request.matchdict.get('organization_id', 0))
        organization = Organization.query.filter_by(id=organization_id).one()
        form = SejTenantForm(self.request.POST, organization_id=organization_id)
        if not form.validate():
            return dict(
                form=form,
                organization=organization,
                route_name=u'登録'
                )

        sej_tenant = merge_session_with_post(SejTenant(), form.data)
        sej_tenant.organization_id = organization_id
        sej_tenant.save()

        self.request.session.flash(u'コンビニ設定を保存しました')
        return HTTPFound(location=route_path('organizations.show', self.request, organization_id=organization_id))

    @view_config(route_name='organizations.sej_tenant.edit', request_method='GET',
                 renderer='altair.app.ticketing:templates/organizations/sej_tenants/edit.html')
    def edit(self):
        organization_id = int(self.request.matchdict.get('organization_id', 0))
        organization = Organization.query.filter_by(id=organization_id).one()
        sej_tenant = SejTenant.filter_by(organization_id=organization_id).first()
        if not sej_tenant:
            raise HTTPNotFound("sej_tenant (%d) is not found" % organization_id)

        form = SejTenantForm(obj=sej_tenant, organization_id=organization_id)
        return dict(
            form=form,
            organization=organization,
            route_name=u'編集'
            )

    @view_config(route_name='organizations.sej_tenant.edit', request_method='POST',
                 renderer='altair.app.ticketing:templates/organizations/sej_tenants/edit.html')
    def edit_post(self):
        organization_id = int(self.request.matchdict.get('organization_id', 0))
        organization = Organization.query.filter_by(id=organization_id).one()
        sej_tenant = SejTenant.filter_by(organization_id=organization_id).first()
        if not sej_tenant:
            raise HTTPNotFound("sej_tenant (%d) is not found" % organization_id)

        form = SejTenantForm(self.request.POST, organization_id=organization_id)
        if not form.validate():
            return dict(
                form=form,
                organization=organization,
                route_name=u'編集'
                )
        sej_tenant = merge_session_with_post(SejTenant(), form.data)
        sej_tenant.save()

        self.request.session.flash(u'コンビニ設定を保存しました')
        return HTTPFound(location=route_path('organizations.show', self.request, organization_id=organization_id))

    @view_config(route_name='organizations.sej_tenant.delete')
    def delete(self):
        organization_id = int(self.request.matchdict.get('organization_id', 0))
        sej_tenant = SejTenant.filter_by(organization_id=organization_id).first()
        if not sej_tenant:
            raise HTTPNotFound("sej_tenant (%d) is not found" % organization_id)

        sej_tenant.delete()

        self.request.session.flash(u'コンビニ設定を削除しました')
        return HTTPFound(location=route_path('organizations.show', self.request, organization_id=organization_id))

@view_defaults(decorator=with_bootstrap, permission="administrator")
class Hosts(BaseView):
    @view_config(route_name='organizations.hosts.new', request_method='GET', renderer='altair.app.ticketing:templates/organizations/hosts/_form.html', xhr=True)
    def new_get(self):
        organization_id = long(self.request.matchdict['organization_id'])
        organization = Organization.query.filter_by(id=organization_id).one()
        form = HostForm()
        return dict(
            organization=organization,
            action=self.request.route_path(self.request.matched_route.name, **self.request.matchdict),
            form=form
            )

    @view_config(route_name='organizations.hosts.new', request_method='POST', renderer='altair.app.ticketing:templates/organizations/hosts/_form.html', xhr=True)
    def new_post(self):
        organization_id = long(self.request.matchdict['organization_id'])
        organization = Organization.query.filter_by(id=organization_id).one()
        form = HostForm(self.request.POST)
        if not form.validate():
            return dict(
                organization=organization,
                action=self.request.route_path(self.request.matched_route.name, **self.request.matchdict),
                form=form
                )
        host = Host(
            organization_id=organization.id,
            host_name=form.host_name.data,
            path=form.path.data,
            base_url=form.base_url.data,
            mobile_base_url=form.mobile_base_url.data
            )
        host.save()
        return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)

    @view_config(route_name='organizations.hosts.edit', request_method='GET', renderer='altair.app.ticketing:templates/organizations/hosts/_form.html', xhr=True)
    def edit_get(self):
        organization_id = long(self.request.matchdict['organization_id'])
        organization = Organization.query.filter_by(id=organization_id).one()
        host_id = long(self.request.matchdict['host_id'])
        host = Host.query.filter_by(organization_id=organization_id, id=host_id).one()
        form = HostForm(obj=host)
        return dict(
            organization=organization,
            action=self.request.route_path(self.request.matched_route.name, **self.request.matchdict),
            form=form
            )

    @view_config(route_name='organizations.hosts.edit', request_method='POST', renderer='altair.app.ticketing:templates/organizations/hosts/_form.html', xhr=True)
    def edit_post(self):
        organization_id = long(self.request.matchdict['organization_id'])
        organization = Organization.query.filter_by(id=organization_id).one()
        host_id = long(self.request.matchdict['host_id'])
        host = Host.query.filter_by(organization_id=organization_id, id=host_id).one()
        form = HostForm(self.request.POST)
        if not form.validate():
            return dict(
                organization=organization,
                action=self.request.route_path(self.request.matched_route.name, **self.request.matchdict),
                form=form
                )
        host.host_name = form.host_name.data
        host.path = form.path.data
        host.base_url = form.base_url.data
        host.mobile_base_url = form.mobile_base_url.data
        host.save()
        return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)

    @view_config(route_name='organizations.hosts.delete')
    def delete(self):
        organization_id = long(self.request.matchdict['organization_id'])
        host_id = long(self.request.matchdict['host_id'])
        host = Host.query.filter_by(organization_id=organization_id, id=host_id).one()
        host.delete()
        return HTTPFound(
            location=self.request.route_path(
                'organizations.show',
                organization_id=organization_id)
            )

@view_defaults(route_name="organizations.mails.new", decorator=with_bootstrap, permission="event_editor",
               renderer="altair.app.ticketing:templates/organizations/mailinfo/new.html")
class MailInfoNewView(BaseView):
    @view_config(request_method="GET")
    def mailinfo_new(self):
        organization_id = int(self.request.matchdict.get("organization_id", 0))
        if unicode(organization_id) != unicode(self.request.context.user.organization_id):
            raise HTTPForbidden
        organization = Organization.get(organization_id)
        mutil = get_mail_utility(self.request, self.request.matchdict["mailtype"])
        template = MailInfoTemplate(self.request, organization, mutil=mutil)
        choice_form = template.as_choice_formclass()()
        formclass = template.as_formclass()
        mailtype = self.request.matchdict["mailtype"]
        form = formclass(**(organization.extra_mailinfo.data.get(mailtype, {}) if organization.extra_mailinfo else {}))
        return {"organization": organization, "form": form, "mailtype": mailtype, "choice_form": choice_form,
                "extra_mailinfo": organization.extra_mailinfo,
                "mutil": mutil, "choices": MailTypeChoices}

    @view_config(request_method="POST")
    def mailinfo_new_post(self):
        mutil = get_mail_utility(self.request, self.request.matchdict["mailtype"])

        organization_id = int(self.request.matchdict.get("organization_id", 0))
        organization = Organization.get(organization_id)
        mailtype = self.request.matchdict["mailtype"]
        template = MailInfoTemplate(self.request, organization, mutil=mutil)
        choice_form = template.as_choice_formclass()()
        formclass = template.as_formclass()
        form = formclass(self.request.POST)
        if not form.validate():
            self.request.session.flash(u"入力に誤りがあります。")
        else:
            mailinfo = mutil.create_or_update_mailinfo(self.request, form.as_mailinfo_data(), organization=organization, kind=mailtype)
            DBSession.add(mailinfo)
            self.request.session.flash(u"メールの付加情報を登録しました")
        return {"organization": organization, "form": form, "mailtype": mailtype, "choice_form": choice_form,
                "mutil": mutil, "choices": MailTypeChoices}
