import codecs
import csv
import io
import logging
from pyramid.view import view_defaults, view_config
from webhelpers.paginate import Page
from sqlalchemy.sql.expression import desc
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.orders.models import Order
from .csvgen import make_csv_gen

logger = logging.getLogger(__name__)

@view_defaults(decorator=with_bootstrap)
class FCAdminEventView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(
        route_name='zea.index',
        renderer='altair.app.ticketing.project_specific.zea:templates/events/index.mako'
        )
    def index(self):
        return {}

    @view_config(
        route_name='zea.detail',
        renderer='altair.app.ticketing.project_specific.zea:templates/events/detail.mako'
        )
    def detail(self):
        return {
            'csvgen': make_csv_gen(self.request),
            'paged_orders': Page(self.context.orders.order_by(desc(Order.id)), page=self.request.GET.get('page')),
            }

    @view_config(
        context='.resources.FCAdminEventResource',
        name='download'
        )
    def download(self):
        response = self.request.response
        encoding = self.request.params.get('encoding', 'CP932')
        encoder = codecs.getencoder(encoding)
        csvgen = make_csv_gen(self.request)
        f = io.BytesIO()
        writer = csv.writer(f)
        block_size = 131072
        errors = 'replace_with_geta'
        def _(orders):
            try:
                writer.writerow([encoder(v, errors=errors)[0] for v in csvgen.header_row()])
                yield f.getvalue()
                f.truncate(0)
                f.seek(0)
                for order in orders:
                    writer.writerow([encoder(v, errors=errors)[0] for v in csvgen.data_row(order)])
                    if f.tell() > block_size:
                        yield f.getvalue()
                        f.truncate(0)
                        f.seek(0)
                yield f.getvalue()
            except:
                logger.exception(u'failed to send CSV file')
        response.content_type = 'text/csv'
        response.content_disposition = 'attachment; filename=download.csv'
        response.app_iter = _(self.context.orders.order_by(desc(Order.id)))
        return response
