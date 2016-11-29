from pyramid.view import view_config
from pyramid.request import Response
from random import randint, choice
import string
import urllib

class SejDummyView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request.decode('shift_jis')

    @view_config(route_name='order.do', request_method='POST')
    def sej_order_do(self):
        try:
            cnt = int(self.request.POST.get('X_ticket_cnt'))
            result = {
                'X_shop_order_id':self.request.POST.get('X_shop_order_id'),
                'X_haraikomi_no':randint(1000000000000, 9999999999999),
                'X_url_info':'http://localhost:8046',
                'iraihyo_id_00':''.join(choice(string.ascii_lowercase + string.digits) for _ in range(32)),
                'X_ticket_cnt':'0{0}'.format(cnt),
                'X_ticket_hon_cnt':'0{0}'.format(cnt),
            }
            for i in range(1, cnt+1):
                result.update({'X_barcode_no_0{0}'.format(i): randint(1000000000000, 9999999999999)})
        except:
            pass
        return Response(body='<SENBDATA>{0}</SENBDATA><SENBDATA>DATA=END</SENBDATA>'.format(urllib.urlencode(result)), status=800)

def setup_routes(config):
    config.add_route('order.do','/order/order.do' )

def main(global_config, **local_config):
    from pyramid.config import Configurator
    settings = dict(global_config)
    config = Configurator(settings=settings)
    config.scan('.')
    config.include(setup_routes)
    return config.make_wsgi_app()
