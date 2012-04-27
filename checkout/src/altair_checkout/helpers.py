from webhelpers.html.builder import literal
from .api import sign_checkout, to_xml

def begin_checkout_form(request):
    action = 'https://my.checkout.rakuten.co.jp/myc/cdodl/1.0/stepin'
    method = 'post'
    accept_charset = 'utf-8'
    return literal('<form action="%(action)s" method="%(method)s" accept-charset="%(accept_charset)s">' %
                   dict(
            action=action,
            method=method,
            accept_charset=accept_charset,
            ))



def render_checkout(request, checkout):
    """
    - checout :class:`Checkout`
    """

    # checkoutをXMLに変換
    xml = to_xml(checkout)

    # 署名作成する
    sig = sign_checkout(xml)

    return literal('<input type="hidden" name="checkout" value="%(checkout)s" />'
                   '<input type="hidden" name="sig" value="%(sig)s" />' % 
                   dict(
            checkout=xml,
            sig=sig,
            ))


def end_checkout_form(request):
    return literal('</form>')

