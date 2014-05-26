import lxml.builder
from decimal import Decimal
from dateutil.parser import parse as parsedate

def must_find(n, path):
    retval = n.find(path)
    if retval is None:
        raise PayloadParseError(u'%s does not exist' % path)
    return retval

def retrieve_item_from_tree(item_n):
    if item_n.tag != u'item':
        raise PayloadParseError(u'unexpected element %s within itemsInfo element' % item_n.tag)
    item_id_n = must_find(item_n, u'itemId')
    item_name_n = must_find(item_n, u'itemName')
    item_numbers_n = must_find(item_n, u'itemNumbers')
    item_fee_n = must_find(item_n, u'itemFee')
    try:
        item_id_str = item_id_n.text.strip()
    except AttributeError:
        raise PayloadParseError(u'empty itemId')
    try:
        item_name_str = item_name_n.text.strip()
    except AttributeError:
        raise PayloadParseError(u'empty itemName')
    try:
        item_numbers_str = item_numbers_n.text.strip()
    except AttributeError:
        raise PayloadParseError(u'empty itemNumbers')
    try:
        item_fee_str = item_fee_n.text.strip()
    except AttributeError:
        raise PayloadParseError(u'empty itemFee')
    try:
        quantity = int(item_numbers_str)
    except (TypeError, ValueError):
        raise PayloadParseError(u'invalid value for itemNumbers: %s' % item_numbers_str)
    try:
        price = Decimal(item_fee_str)
    except TypeError:
        raise PayloadParseError(u'invalid value for itemFee: %s' % item_fee_str)
    item = {
        'id': item_id_str,
        'name': item_name_str,
        'quantity': quantity,
        'price': price,
        }
    return item

def parse_order(root):
    order_cart_id_n = must_find(root, u'orderCartId')
    order_complete_url_n = must_find(root, u'orderCompleteUrl')
    order_failed_url_n = must_find(root, u'orderFailedUrl')
    order_total_fee_n = must_find(root, u'orderTotalFee')
    is_t_mode_n = must_find(root, u'isTMode')
    items_info_n = must_find(root, u'itemsInfo')

    try:
        order_cart_id_str = order_cart_id_n.text.strip()
    except AttributeError:
        raise PayloadParseError(u'empty orderCartId')
    try:
        order_complete_url_str = order_complete_url_n.text.strip()
    except AttributeError:
        raise PayloadParseError(u'empty orderCompleteUrl')
    try:
        order_failed_url_str = order_failed_url_n.text.strip()
    except AttributeError:
        raise PayloadParseError(u'empty orderFailedUrl')
    try:
        order_total_fee_str = order_total_fee_n.text.strip()
    except AttributeError:
        raise PayloadParseError(u'empty orderTotalFee')

    is_t_mode_str = is_t_mode_n.text.strip() if is_t_mode_n.text else u''

    try:
        total_amount = Decimal(order_total_fee_str)
    except AttributeError:
        raise PayloadParseError(u'invalid value for orderTotalFee: %s' % order_total_fee_str)

    items = [
        retrieve_item_from_tree(item_n)
        for item_n in items_info_n
        ]
    return {
        'order_cart_id': order_cart_id_str,
        'order_complete_url': order_complete_url_str,
        'order_failed_url': order_failed_url_str,
        'total_amount': total_amount,
        'test_mode': is_t_mode_str,
        'items': items,
        }

def build_payload_for_cart_confirming(order, cart_confirmation_id, openid_claimed_id):
    E = lxml.builder.E
    payload = E.cartConfirmationRequest(
        E.openId(openid_claimed_id),
        E.carts(
            E.cart(
                E.cartConfirmationId(cart_confirmation_id),
                E.orderCartId(order['order_cart_id']),
                E.orderTotalFee(unicode(order['total_amount'].quantize(0))),
                E.items(*(
                    E.item(
                        E.itemId(item['id']),
                        E.itemName(item['name']),
                        E.itemNumbers(unicode(item['quantity'])),
                        E.itemFee(unicode(item['price'].quantize(0)))
                        )
                    for item in order['items']
                    )),
                E.isTMode(order['test_mode']),
                )
            )
        )
    return payload

def parse_cart_confirming_callback_response(xml):
    if xml.tag != u'cartConfirmationResponse':
        raise PayloadParseError(u'root element must be cartConfirmationResponse')

    carts_n = xml.find('carts')
    if carts_n is None:
        raise PayloadParseError(u'missing <carts> element under cartConfirmationResponse')
    carts = []
    for cart_n in carts_n:
        if cart_n.tag != u'cart':
            raise PayloadParseError(u'unexpected element <%s> under <carts>' % cart_n.tag)
        items_n = must_find(cart_n, 'items')
        cart_confirmation_id_n = must_find(cart_n, 'cartConfirmationId')
        order_cart_id_n = must_find(cart_n, 'orderCartId')
        order_items_total_fee_n = must_find(cart_n, 'orderItemsTotalFee')
        try:
            cart_confirmation_id_str = cart_confirmation_id_n.text.strip()
        except AttributeError:
            raise PayloadParseError(u'empty cartConfirmationId')
        try:
            order_cart_id_str = order_cart_id_n.text.strip()
        except AttributeError:
            raise PayloadParseError(u'empty orderCartId')
        try:
            order_items_total_fee_str = order_items_total_fee_n.text.strip()
        except AttributeError:
            raise PayloadParseError(u'empty orderItemsTotalFee')
        try:
            total_amount = Decimal(order_items_total_fee_str)
        except AttributeError:
            raise PayloadParseError(u'invalid value for orderTotalFee: %s' % order_items_total_fee_str)

        items = [
            retrieve_item_from_tree(item)
            for item in items_n
            ]
        cart = {
            'cart_confirmation_id': cart_confirmation_id_str,
            'order_cart_id': order_cart_id_str,
            'total_fee': total_fee,
            'items': items,
            }
        carts.append(cart)
    return {
        'carts': carts,
        }
        
def build_payload_for_completion_notification(order, order_id, order_control_id, order_date, used_point, openid_claimed_id):
    E = lxml.builder.E
    payload = E.orderCompleteRequest(
        E.orderId(order_id),
        E.orderControlId(order_control_id),
        E.openId(openid_claimed_id),
        E.orderCartId(order['order_cart_id']),
        E.usedPoint(unicode(used_point.quantize(0))),
        E.orderDate(order_date.strftime('%Y-%m-%d %H:%M:%S').decode('utf-8')),
        E.orderTotalFee(unicode(order['total_amount'].quantize(0))),
        E.items(*[
            E.item(
                E.itemId(item['id']),
                E.itemName(item['name']),
                E.itemNumbers(unicode(item['quantity'])),
                E.itemFee(unicode(item['price'].quantize(0)))
                )
            for item in order['items']
            ]),
        E.isTMode(order['test_mode'])
        )
    return payload

def parse_completion_notification_callback_response(xml):
    if xml.tag != u'orderCompleteResponse':
        raise PayloadParseError(u'root element must be orderCompleteResponse')

    result_n = must_find(xml, u'result')
    complete_time_n = must_find(xml, u'completeTime')

    try:
        result = int(result_n.text.strip())
    except AttributeError:
        raise PayloadParseError(u'empty <result> element')
    except (TypeError, ValueError):
        raise PayloadParseError(u'invalid value for <result> element')

    try:
        complete_time = parsedate(complete_time_n.text.strip())
    except AttributeError:
        raise PayloadParseError(u'empty <completeTime> element')
    except ValueError:
        raise PayloadParseError(u'invalid value for <completeTime> element')
    return {
        'result': result,
        'complete_time': complete_time,
        }

def parse_settlement_request(xml):
    access_key_n = must_find(xml, u'accessKey')
    request_id_n = must_find(xml, u'requestId')
    orders_n = must_find(xml, u'orders')

    try:
        access_key_str = access_key_n.text.strip()
    except AttributeError:
        raise PayloadParseError(u'empty accessKey')

    try:
        request_id_str = request_id_n.text.strip()
    except AttributeError:
        raise PayloadParseError(u'empty requestId')

    orders = []
    for order_n in orders_n:
        if order_n.tag != u'order':
            raise PayloadParseError(u'unexpected element <%s> found under <orders>' % order_n.tag)

        order_control_id_n = must_find(order_n, u'orderControlId')
        try:
            order_control_id_str = order_control_id_n.text.strip()
        except AttributeError:
            raise PayloadParseError(u'empty orderControlId') 
        order = {
            'order_control_id': order_control_id_str,
            }
        orders.append(order)

    return {
        'access_key': access_key_str,
        'request_id': request_id_str,
        'orders': orders,
        }

def build_settlement_response(orders, status_code, error_code):
    E = lxml.builder.E
    failure_count = sum(bool(order.get('error_code')) for order in orders)
    payload = E.root(
        E.statusCode(unicode(status_code)),
        E.acceptNumber(u'%d' % len(orders)),
        E.successNumber(u'%d'% (len(orders) - failure_count)),
        E.failedNumber(u'%d' % failure_count),
        E.orders(*[
            E.order(
                E.orderControlId(order['order_control_id']),
                *([E.orderErrorCode(u'%d' % order['order_error_code'])] if order.get('order_error_code') is not None else [])
                )
            for order in orders
            ]),
        *([E.apiErrorCode(u'%03d' % error_code)] if error_code is not None else [])
        )
    return payload
