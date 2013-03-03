import isodate
from datetime import datetime

def get_cms_data(request, organization, event, now=None):
    assert event.organization_id == organization.id
    now = now or datetime.now()
    return {
        'organization': {'id': organization.id, 'short_name': organization.short_name}, 
        'events':[event.get_cms_data()],
        'created_at':isodate.datetime_isoformat(now),
        'updated_at':isodate.datetime_isoformat(now),
        }
    

