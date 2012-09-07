# -*- coding: utf-8 -*-
import logging
logger = logging.getLogger(__name__)

from ticketing.fanstatic import with_bootstrap
from pyramid.view import view_config, view_defaults
from ticketing.views import BaseView
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPCreated
from ticketing.mails.forms import MailInfoTemplate
from ticketing.models import DBSession
from ticketing.mails.api import get_mail_utility

from ticketing.core.models import Event, MailTypeChoices


@view_config(decorator=with_bootstrap, permission="authenticated", 
             route_name="events.mailinfo.index")
def mailinfo_index_view(context, request):
    event_id = request.matchdict["event_id"]
    return HTTPFound(request.route_url("events.mailinfo.edit", event_id=event_id, mailtype=MailTypeChoices[0][0]))

@view_defaults(decorator=with_bootstrap, permission="authenticated", 
               route_name="events.mailinfo.edit", 
               renderer="ticketing:templates/events/mailinfo/new.html")
class MailInfoNewView(BaseView):
    @view_config(request_method="GET")
    def mailinfo_new(self):
        event = Event.filter_by(organization_id=self.context.user.organization_id,
                                id=self.request.matchdict["event_id"]).first()
        if event is None:
            raise HTTPNotFound('event id %s is not found' % self.request.matchdict["event_id"])

        template = MailInfoTemplate(self.request, event.organization)
        choice_form = template.as_choice_formclass()()
        formclass = template.as_formclass()
        mailtype = self.request.matchdict["mailtype"]
        form = formclass(**(event.extra_mailinfo.data.get(mailtype, {}) if event.extra_mailinfo else {}))
        return {"event": event, 
                "form": form, 
                "organization": event.organization, 
                "mailtype": self.request.matchdict["mailtype"], 
                "choices": MailTypeChoices, 
                "choice_form": choice_form}

    @view_config(request_method="POST")
    def mailinfo_new_post(self):
        logger.debug("mailinfo.post: %s" % self.request.POST)
        mutil = get_mail_utility(self.request, self.request.matchdict["mailtype"])

        event = Event.filter_by(organization_id=self.context.user.organization_id,
                                id=self.request.matchdict["event_id"]).first()
        if event is None:
            raise HTTPNotFound('event id %s is not found' % self.request.matchdict["event_id"])
        template = MailInfoTemplate(self.request, event.organization)
        choice_form = template.as_choice_formclass()()
        form = template.as_formclass()(self.request.POST)
        if not form.validate():
            self.request.session.flash(u"入力に誤りがあります。")
        else:
            mailtype = self.request.matchdict["mailtype"]
            mailinfo = mutil.create_or_update_mailinfo(self.request, form.as_mailinfo_data(), event=event, kind=mailtype)
            logger.debug("mailinfo.data: %s" % mailinfo.data)
            DBSession.add(mailinfo)
            self.request.session.flash(u"メールの付加情報を登録しました")

        return {"event": event, 
                "form": form, 
                "choice_form": choice_form, 
                "organization": event.organization, 
                "mailtype": self.request.matchdict["mailtype"], 
                "choices": MailTypeChoices}
