# encoding: utf-8

from ticketing.users.models import UserPointAccountTypeEnum

point_types = {
    UserPointAccountTypeEnum.Rakuten.v: u'楽天スーパーポイント'
    }

def format_point_type(type_value):
    retval = None
    try:
        retval = point_types.get(int(type_value))
    except (TypeError, ValueError):
        pass
    return retval or u'-'

