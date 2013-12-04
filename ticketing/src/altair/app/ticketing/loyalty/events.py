class PointGrantingFailed(object):
    def __init__(self, request, point_grant_history_entry):
        self.request = request
        self.point_grant_history_entry = point_grant_history_entry

def notify_point_granting_failed(request, point_grant_history_entry):
    event = PointGrantingFailed(request, point_grant_history_entry)
    request.registry.notify(event)
