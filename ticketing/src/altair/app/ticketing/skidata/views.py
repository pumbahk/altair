# -*- coding: utf-8 -*-

from altair.app.ticketing.views import BaseView
from altair.app.ticketing.fanstatic import with_bootstrap
from pyramid.view import view_config, view_defaults
from altair.app.ticketing.skidata.models import SkidataProperty, SkidataPropertyTypeEnum
from altair.app.ticketing.skidata.forms import SkidataPropertyForm
from pyramid.httpexceptions import HTTPFound
from altair.sqlahelper import get_db_session
from sqlalchemy.orm.exc import NoResultFound


@view_defaults(decorator=with_bootstrap, permission="event_editor")
class SkidataPropertyView(BaseView):
    @view_config(route_name='skidata.property.show',
                 request_method='GET',
                 renderer='altair.app.ticketing:templates/skidata/property/show.html')
    def show(self):
        props = SkidataProperty.find_all_by_org_id(self.context.user.organization.id,
                                                   get_db_session(self.request, name='slave'))
        return dict(
            props_for_sales_segment_group=[p for p in props if
                                           p.prop_type == SkidataPropertyTypeEnum.SalesSegmentGroup.v],
            props_for_product_item=[p for p in props if p.prop_type == SkidataPropertyTypeEnum.ProductItem.v],
        )

    @view_config(route_name='skidata.property.new',
                 request_method='GET',
                 renderer='altair.app.ticketing:templates/skidata/property/form.html')
    def show_new_prop_form(self):
        prop_type = self._get_prop_type_by_uri()
        if prop_type is None:
            self.request.session.flash(u'不正なページ遷移です。')
            return HTTPFound(location=self.request.route_path('skidata.property.show'))

        return dict(prop_type=prop_type, form=SkidataPropertyForm())

    @view_config(route_name='skidata.property.new',
                 request_method='POST',
                 renderer='altair.app.ticketing:templates/skidata/property/form.html')
    def create_property(self):
        prop_type = self._get_prop_type_by_uri()
        if prop_type is None:
            self.request.session.flash(u'不正なページ遷移です。')
            return HTTPFound(location=self.request.route_path('skidata.property.show'))

        form = SkidataPropertyForm(formdata=self.request.POST)
        if not form.validate():
            self.request.session.flash(u'入力内容に誤りがあります。')
            return dict(prop_type=prop_type, form=form)

        prop = SkidataProperty.insert_new_property(self.context.user.organization.id, form.name.data,
                                                   form.value.data, prop_type.v)
        self.request.session.flash(u'登録完了しました[id={}]'.format(prop.id))
        return HTTPFound(location=self.request.route_path('skidata.property.show'))

    def _get_prop_type_by_uri(self):
        if self.request.matchdict['prop_type'] == SkidataPropertyTypeEnum.SalesSegmentGroup.k:
            return SkidataPropertyTypeEnum.SalesSegmentGroup
        if self.request.matchdict['prop_type'] == SkidataPropertyTypeEnum.ProductItem.k:
            return SkidataPropertyTypeEnum.ProductItem
        return None

    @view_config(route_name='skidata.property.edit',
                 request_method='GET',
                 renderer='altair.app.ticketing:templates/skidata/property/form.html')
    def show_edit_prop_form(self):
        try:
            prop = SkidataProperty.find_by_id(self.request.matchdict['id'], get_db_session(self.request, name='slave'))
        except NoResultFound:
            self.request.session.flash(u'対象のデータが存在しません')
            return HTTPFound(location=self.request.route_path('skidata.property.show'))

        return dict(prop_id=prop.id, form=SkidataPropertyForm(skidata_property=prop))

    @view_config(route_name='skidata.property.edit',
                 request_method='POST',
                 renderer='altair.app.ticketing:templates/skidata/property/form.html')
    def update_property(self):
        prop_id = self.request.matchdict['id']

        form = SkidataPropertyForm(formdata=self.request.POST)
        if not form.validate():
            self.request.session.flash(u'入力内容に誤りがあります。')
            return dict(prop_id=prop_id, form=form)

        try:
            prop = SkidataProperty.update_property(prop_id, form.name.data, form.value.data)
        except NoResultFound:
            self.request.session.flash(u'対象のデータが存在しません')
            return HTTPFound(location=self.request.route_path('skidata.property.show'))

        self.request.session.flash(u'更新しました[id={}]'.format(prop.id))
        return HTTPFound(location=self.request.route_path('skidata.property.show'))

    @view_config(route_name='skidata.property.delete', request_method='POST')
    def delete_property(self):
        prop_id = self.request.matchdict['id']
        try:
            SkidataProperty.delete_property(prop_id)
            self.request.session.flash(u'対象のプロパティを削除しました[id={}]'.format(prop_id))
        except:
            self.request.session.flash(u'対象のデータが存在しません')
        return HTTPFound(location=self.request.route_path('skidata.property.show'))
