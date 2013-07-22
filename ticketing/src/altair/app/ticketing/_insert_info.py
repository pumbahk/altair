from mako.template import Template
from altair.app.ticketing.core.models import ExtraMailInfo;

def main(*args, **kwargs):
    tmpl = u"""
from altair.app.ticketing.core.models import ExtraMailInfo;
from altair.app.ticketing.models import DBSession
import transaction

info = ExtraMailInfo.query.filter_by(organization_id=${organization_id},  event_id=${event_id},  performance_id=${performance_id}).first()
data = ${data}
if info is None:
    DBSession.add(ExtraMailInfo(organization_id=${organization_id},  event_id=${event_id},  performance_id=${performance_id}, data=data))
else:
    info.data = data
    info.data.changed()
    DBSession.add(info)
transaction.commit()
    """
    template = Template(tmpl)

    def as_script(template, info):
        return template.render(organization_id=info.organization_id,
                               event_id=info.event_id,
                               performance_id=info.performance_id,
                               data=info.data
                               )

    candidates = ((1, None, None), 
                  (2, None, None), 
                  (3, None, None), 
                  (4, None, None), 
                  (13, None, None), 
                  (15, None, None), 
                  (19, None, None), 
                  (19, 457, None))
    for organization_id, event_id, performance_id in candidates:
        info = ExtraMailInfo.query.filter_by(
            organization_id=organization_id,
            event_id=event_id,
            performance_id=performance_id).one()
        print as_script(template, info)
    return 0
