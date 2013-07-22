from .interfaces import IPertistentProfile
from .interfaces import IPertistentProfileFactory
import altair.app.ticketing.core.models as c_models
from altair.app.ticketing.models import DBSession
from zope.interface import implementer

def get_main_ordered_product_from_order(order):
    return order.items[0].ordered_product_items[0]

@implementer(IPertistentProfile)
class PersistentProfileForOrder(object):
    def __init__(self, request, attr_names, compat_attr_map):
        self.request = request
        self.attr_names = attr_names
        self.compat_attr_map = compat_attr_map
    
    def get_user_profile(self, order):
        retval = {}
        attrs = dict(get_main_ordered_product_from_order(order).attributes)

        for attr_name, old_attr_name in self.compat_attr_map.items():
            if attr_name not in attrs and old_attr_name in attrs:
                attrs[attr_name] = attrs[old_attr_name]

        for k, v in attrs.items():
            refs = k.split('.') 
            ns = retval
            last = refs.pop()
            for ref in refs:
                ns = ns.setdefault(ref, {})
            ns[last] = v

        for attr_name, old_attr_name in self.compat_attr_map.items():
            refs = attr_name.split('.')
            value = retval
            for ref in refs:
                if not isinstance(value, dict):
                    value = None
                    break
                value = value.get(ref)
                if value is None:
                    break
            if value is not None and old_attr_name not in retval:
                retval[old_attr_name] = value

        return retval

    def set_user_profile(self, order, user_profile):
        member_type = user_profile['member_type']
        ordered_product_item = c_models.OrderedProductItem.query.filter(
            c_models.OrderedProduct.order==order
        ).filter(
            c_models.OrderedProduct.product_id==member_type
        ).filter(
            c_models.OrderedProductItem.ordered_product_id==c_models.OrderedProduct.id
        ).first()

        user_profile = dict(user_profile)
        for attr_name, old_attr_name in self.compat_attr_map.items():
            refs = attr_name.split('.')
            value = user_profile
            for ref in refs:
                if not isinstance(value, dict):
                    value = None
                    break
                value = value.get(ref)
                if value is None:
                    break
            if value is None and old_attr_name in user_profile:
                last = refs.pop()
                ns = user_profile
                for ref in refs:
                    ns = ns.get(ref)
                    if not isinstance(ns, dict):
                        ns = ns[ref] = {}
                ns[last] = user_profile[old_attr_name]

        for attr_name in self.attr_names:
            # traversing the dictionary
            refs = attr_name.split('.')
            value = user_profile
            for ref in refs:
                if not isinstance(value, dict):
                    raise TypeError
                value = value.get(ref)
                if value is None:
                    break
            if value is not None:
                # store the value
                DBSession.add(
                    c_models.OrderedProductAttribute(
                        ordered_product_item=ordered_product_item,
                        name=attr_name,
                        value=value)
                    )

@implementer(IPertistentProfileFactory)
class PersistentProfileFactory(object):
    attr_names = [
        u'cont',
        u'member_type',
        u'old_id_number',
        u'year',
        u'month',
        u'day',
        u'sex',
        u'fax', 
        ]

    compat_attr_map = {
        u'extra.mail_permission': u'mail_permission',
        u'extra.publicity': u'publicity',
        }

    Class = PersistentProfileForOrder
    def __call__(self, request):
        return self.Class(request, self.attr_names, self.compat_attr_map)
