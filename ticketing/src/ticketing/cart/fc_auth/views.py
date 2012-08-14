from repoze.who.api import get_api as get_who_api
from pyramid.view import view_config

class LoginView(object):
    def __init__(self, request):
        self.request = request


    @view_config(request_method="GET")
    def login_form(self):
        pass


    @view_config(request_method="POST")
    def login(self):
        who_api = get_who_api(self.request.environ)
        membership = self.context.membership
        identity = {
            'membership': membership,
            'username': username,
            'password': password,
        }
        authenticated, headers = who_api.login(identity)

        if authenticated is None:
            return {}

        return_to_url = self.return_to_url
        res = HTTPFound(location=return_to_url)
        res.header_list.extend(headers)

        return res

