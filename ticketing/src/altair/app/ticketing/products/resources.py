# -*- coding: utf-8 -*-

from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy.orm.exc import NoResultFound

from altair.app.ticketing.resources import TicketingAdminResource
from altair.app.ticketing.core.models import Organization, Performance, SalesSegment, Product, ProductItem


class ProductResource(TicketingAdminResource):

    def __init__(self, request):
        super(ProductResource, self).__init__(request)
        self.product_id = None

        if not self.user:
            return

        try:
            self.product_id = long(self.request.matchdict.get('product_id'))
        except (TypeError, ValueError):
            raise HTTPNotFound()

    @reify
    def product(self):
        try:
            p = Product.query.join(SalesSegment).filter(
                    Product.id==self.product_id,
                    SalesSegment.organization_id==self.user.organization_id
                    ).one()
        except NoResultFound:
            raise HTTPNotFound()
        return p


class ProductAPIResource(TicketingAdminResource):
    pass


class ProductShowResource(TicketingAdminResource):
    def __init__(self, request):
        super(ProductShowResource, self).__init__(request)
        self.sales_segment_id = None

        if not self.user:
            return

        try:
            self.sales_segment_id = long(self.request.matchdict.get('sales_segment_id'))
        except (TypeError, ValueError):
            raise HTTPNotFound()

    @reify
    def sales_segment(self):
        try:
            s = SalesSegment.query.join(Organization).filter(
                    SalesSegment.id==self.sales_segment_id,
                    Organization.id==self.user.organization_id
                    ).one()
        except NoResultFound:
            raise HTTPNotFound()
        return s


class ProductItemResource(TicketingAdminResource):

    def __init__(self, request):
        super(ProductItemResource, self).__init__(request)
        self.product_item_id = None

        if not self.user:
            return

        try:
            self.product_item_id = long(self.request.matchdict.get('product_item_id'))
        except (TypeError, ValueError):
            raise HTTPNotFound()

    @reify
    def product_item(self):
        try:
            p = ProductItem.query.join(ProductItem.product, Product.sales_segment).filter(
                    ProductItem.id==product_item_id,
                    SalesSegment.organization_id==self.user.organization_id
                    ).one()
        except NoResultFound:
            raise HTTPNotFound()
        return p


class ProductCreateResource(TicketingAdminResource):

    def __init__(self, request):
        super(ProductCreateResource, self).__init__(request)
        self.performance_id = None
        self.sales_segment_id = None

        if not self.user:
            return

        try:
            self.performance_id = long(self.request.params.get('performance_id'))
        except (TypeError, ValueError):
            pass

        try:
            self.sales_segment_id = long(self.request.params.get('sales_segment_id'))
        except (TypeError, ValueError):
            pass

    @reify
    def performance(self):
        p = None
        if self.performance_id is not None:
            p = Performance.get(self.performance_id, self.user.organization_id)
            if not p:
                raise HTTPNotFound()
        return p

    @reify
    def sales_segment(self):
        s = None
        if self.sales_segment_id is not None:
            try:
                s = SalesSegment.query.join(Organization).filter(
                        SalesSegment.id==self.sales_segment_id,
                        Organization.id==self.user.organization_id
                        ).one()
            except NoResultFound:
                raise HTTPNotFound()
        return s
