# -*- coding: utf-8 -*-

from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.views import BaseView
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.view import view_config, view_defaults
from . import helpers as h

from .forms import PassportForm, PassportNotAvailableTermForm
from ..models import Passport, PassportNotAvailableTerm


@view_defaults(decorator=with_bootstrap, permission='master_editor')
class PassportView(BaseView):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name='passport.index', renderer='altair.app.ticketing:templates/passport/index.html')
    def index(self):
        return dict(
            passports=self.context.passports
        )

    @view_config(route_name='passport.show', renderer='altair.app.ticketing:templates/passport/show.html')
    def show(self):
        return dict(
            passport=self.context.passport
        )

    @view_config(route_name='passport.new', request_method="GET",
                 renderer='altair.app.ticketing:templates/passport/form.html')
    def new(self):
        form = PassportForm(organization_id=self.context.user.organization_id)
        form.configure()
        return dict(form=form)

    @view_config(route_name='passport.new', request_method="POST",
                 renderer='altair.app.ticketing:templates/passport/form.html')
    def new_post(self):
        form = PassportForm(organization_id=self.context.user.organization_id, formdata=self.request.POST)
        if not form.validate():
            form.configure()
            return dict(form=form)

        # TODO passport organizatoin_idをGETから
        params = form.data
        passport = Passport(
            name=params["name"],
            organization_id=self.context.user.organization_id,
            performance_id=params["performance_id"],
            available_day=params["available_day"],
            daily_passport=params["daily_passport"],
            is_valid=params["is_valid"],
        )
        passport.save()
        self.request.session.flash(u'パスポートを登録しました')
        return HTTPFound(location=self.request.route_path("passport.index"))

    @view_config(route_name='passport.edit', request_method="GET",
                 renderer='altair.app.ticketing:templates/passport/form.html')
    def edit(self):
        passport = self.context.passport
        if passport is None:
            raise HTTPNotFound("passport is not found")

        form = PassportForm(organization_id=self.context.user.organization_id,
                            name=passport.name,
                            available_day=passport.available_day,
                            daily_passport=passport.daily_passport,
                            is_valid=passport.is_valid,
                            )
        form.configure()
        if passport.performance:
            form.performance_id.data = passport.performance.id
        return dict(form=form, passport=passport)

    @view_config(route_name='passport.edit', request_method="POST",
                 renderer='altair.app.ticketing:templates/passport/form.html')
    def edit_post(self):
        passport = self.context.passport
        if passport is None:
            raise HTTPNotFound("passport is not found. edit post")

        form = PassportForm(organization_id=self.context.user.organization_id,
                            formdata=self.request.POST)

        if not form.validate():
            form.configure()
            return dict(form=form, passport=passport)

        params = form.data
        passport.name = params["name"]
        passport.available_day = params["available_day"]
        passport.performance_id = params["performance_id"]
        passport.daily_passport = params["daily_passport"]
        passport.is_valid = params["is_valid"]
        passport.organization_id = self.context.user.organization_id
        passport.save()
        self.request.session.flash(u'パスポートを更新しました')
        return HTTPFound(location=self.request.route_path("passport.show", passport_id=passport.id))

    @view_config(route_name='passport.delete')
    def delete(self):
        passport = self.context.passport
        if passport is None:
            raise HTTPNotFound("passport is not found. delete")
        # elif passport > 0:
        #     self.request.session.flash(u'販売されているため消せません')
        else:
            passport.delete()
            self.request.session.flash(u'パスポートを削除しました')

        return HTTPFound(location=self.request.route_path("passport.index"))


@view_defaults(decorator=with_bootstrap, permission='master_editor')
class TermView(BaseView):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name='term.index', renderer='altair.app.ticketing:templates/passport/term/index.html')
    def index(self):
        return dict(
            passport=self.context.passport,
            terms=self.context.terms,
            h=h
        )

    @view_config(route_name='term.show', renderer='altair.app.ticketing:templates/passport/term/show.html')
    def show(self):
        term = self.context.term
        return dict(
            passport=term.passport,
            term=term
        )

    @view_config(route_name='term.new', request_method="GET",
                 renderer='altair.app.ticketing:templates/passport/term/form.html')
    def new(self):
        form = PassportNotAvailableTermForm()
        return dict(form=form, passport=self.context.passport)

    @view_config(route_name='term.new', request_method="POST",
                 renderer='altair.app.ticketing:templates/passport/term/form.html')
    def new_post(self):
        form = PassportNotAvailableTermForm(formdata=self.request.POST)
        if not form.validate():
            return dict(form=form)

        params = form.data
        term = PassportNotAvailableTerm(
            start_on=params["start_on"],
            end_on=params["end_on"],
            passport_id=self.request.matchdict['passport_id']
        )
        term.save()
        self.request.session.flash(u'パスポート入場不可期間を登録しました')
        return HTTPFound(
            location=self.request.route_path("term.index", passport_id=self.request.matchdict['passport_id']))

    @view_config(route_name='term.edit', request_method="GET",
                 renderer='altair.app.ticketing:templates/passport/term/form.html')
    def edit(self):
        term = self.context.term
        if term is None:
            raise HTTPNotFound("term is not found")

        form = PassportNotAvailableTermForm(
            start_on=term.start_on,
            end_on=term.end_on
        )
        return dict(form=form, passport=term.passport, term=term)

    @view_config(route_name='term.edit', request_method="POST",
                 renderer='altair.app.ticketing:templates/passport/term/form.html')
    def edit_post(self):
        term = self.context.term
        if term is None:
            raise HTTPNotFound("term is not found. edit post")
        form = PassportNotAvailableTermForm(formdata=self.request.POST)
        if not form.validate():
            return dict(form=form, passport=term.passport, term=term)

        params = form.data
        term.start_on = params["start_on"]
        term.end_on = params["end_on"]
        term.save()
        self.request.session.flash(u'パスポート入場不可期間を更新しました')
        return HTTPFound(location=self.request.route_path("term.show", term_id=term.id))

    @view_config(route_name='term.delete')
    def delete(self):
        term = self.context.term
        pasport_id = term.passport.id
        if term is None:
            raise HTTPNotFound("term is not found. delete")
        # elif passport > 0:
        #     self.request.session.flash(u'販売されているため消せません')
        else:
            term.delete()
            self.request.session.flash(u'パスポート入場不可期間を削除しました')

        return HTTPFound(location=self.request.route_path("term.index", passport_id=pasport_id))
