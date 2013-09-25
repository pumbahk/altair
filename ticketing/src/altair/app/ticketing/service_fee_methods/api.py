#-*- coding: utf-8 -*-
from altair.app.ticketing.core.models import ServiceFeeMethod

class SystemFeeDefaultDoesNotExist(Exception):
    pass

class SystemFeeDefaultDuplicated(Exception):
    pass

def get_system_fee_default(organization_id):
    service_fee_methods = ServiceFeeMethod.filter_by(organization_id=organization_id,
                                                     system_fee_default=True)
    count = service_fee_methods.count()
    if count == 1:
        service_fee_method = service_fee_methods[0]
        return service_fee_method.fee, service_fee_method.fee_type
    elif count == 0:
        raise SystemFeeDefaultDoesNotExist()
    elif count > 1:
        raise SystemFeeDefaultDuplicated()
    else:
        assert False, 'system fee default count = {0}'.format(count)
