# encoding: utf-8

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound
from altair.app.ticketing.views import BaseView

from altair.app.ticketing.fanstatic import with_bootstrap
import webhelpers.paginate as paginate
from .models import MailMagazine, MailSubscription, MailSubscriptionStatus

from .forms import MailMagazineForm
import helpers

@view_defaults(decorator=with_bootstrap,  permission='administrator')
class MailMagazinesView(BaseView):
    @view_config(route_name='mailmags.index', renderer='altair.app.ticketing:templates/mailmags/index.html')
    def index(self):
        mailmag_query = MailMagazine.query.filter_by(organization=self.context.organization)
        return dict(
            mailmags=paginate.Page(
                mailmag_query,
                page=int(self.request.params.get('page', '0')),
                items_per_page=25,
                url=paginate.PageURL_WebOb(self.request)
                )
            )

    @view_config(route_name='mailmags.edit', renderer='altair.app.ticketing:templates/mailmags/edit.html', request_method='GET')
    def edit(self):
        mailmag_id = self.request.matchdict['id']
        mailmag = MailMagazine.query.filter_by(id=mailmag_id, organization=self.request.context.organization).one()
        return dict(
            mailmag=mailmag,
            mailmag_form=MailMagazineForm(
                name=mailmag.name,
                description=mailmag.description
                )
            )

    @view_config(route_name='mailmags.edit', renderer='altair.app.ticketing:templates/mailmags/edit.html', request_method='POST')
    def edit_post(self):
        mailmag_form = MailMagazineForm(self.request.params)
        mailmag_id = self.request.matchdict.get('id', mailmag_form.id.data)
        mailmag = MailMagazine.query.filter_by(id=mailmag_id, organization=self.request.context.organization).one()
        if mailmag_form.validate():
            mailmag.name = mailmag_form.name.data
            mailmag.description = mailmag_form.description.data
            mailmag.save()
            self.request.session.flash(u'メールマガジンの情報を更新しました')
        return dict(
            mailmag=mailmag,
            mailmag_form=mailmag_form
            )

    @view_config(route_name='mailmags.show', renderer='altair.app.ticketing:templates/mailmags/show.html')
    def show(self):
        mailmag_id = self.request.matchdict.get('id')
        mailmag = MailMagazine.query.filter_by(id=mailmag_id, organization=self.request.context.organization).one()
        search_text = self.request.params.get('search_text')
        mail_subscriptions_query = MailSubscription.query.filter_by(segment=mailmag)
        if search_text:
            mail_subscriptions_query = mail_subscriptions_query.filter(MailSubscription.email.like(search_text + '%'))
        mail_subscriptions = paginate.Page(
            mail_subscriptions_query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=25,
            url=paginate.PageURL_WebOb(self.request)
            )
        return dict(
            mailmag=mailmag,
            mail_subscriptions=mail_subscriptions,
            search_text=search_text or u'',
            h=helpers
            )

@view_defaults(decorator=with_bootstrap,  permission='administrator')
class MailSubscriptionsView(BaseView):
    @view_config(route_name='mailmags.subscriptions.edit', request_method='POST')
    def edit(self):
        mailmag_id = self.request.matchdict.get('id', self.request.params.get('id'))
        mailmag = MailMagazine.query.filter_by(id=mailmag_id, organization=self.request.context.organization).one()
        search_text = self.request.params.get('search_text')
        mail_subscription_ids = self.request.params.getall('mail_subscription_id')
        action = self.request.params.get('action')
        for k, v in self.request.params.items():
            if k.startswith('do_'):
                action = k[3:]
        if action == 'set_status':
            status = self.request.params.get('status')
            MailSubscription.query \
                .filter(MailSubscription.id.in_(mail_subscription_ids)) \
                .update(values=dict(status=status), synchronize_session=False)
        elif action == 'clear':
            search_text = None
        return HTTPFound(location=self.request.route_path(
            'mailmags.show',
            id=mailmag_id,
            _query=dict(
                page=self.request.params.get('page'),
                search_text=search_text or u''
                )
            ))
