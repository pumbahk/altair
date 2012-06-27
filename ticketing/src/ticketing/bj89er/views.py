from . import schemas
import ticketing.core.models as c_models
import ticketing.cart.helpers as h
import sqlalchemy as sa


class IndexView(object):
    def __init__(self, request):
        self.request = request
        self.context = request.context


    def __call__(self):
        return dict()

    def get(self):
        event = c_models.Event.query.filter_by(id=self.context.event_id).one()

        salessegment = self.context.get_sales_segument()

        query = c_models.Product.query
        #query = query.filter(c_models.Product.id.in_(q))
        query = query.order_by(sa.desc("price"))
        query = h.products_filter_by_salessegment(query, salessegment)


        products = [dict(name=p.name, price=h.format_number(p.price, ","), id=p.id)
                    for p in query]
        return dict(products=products)

    def post(self):
        return dict()
