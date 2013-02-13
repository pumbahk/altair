from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    Host,
    )


@view_config(route_name='home', renderer='cmsmobile:templates/top/top.mako')
def main(request):
    try:
        one = DBSession.query(Host).first()
    except DBAPIError:
        return Response("DB error!", content_type='text/plain', status_int=500)
    return {'one': one, 'project': 'cmsmobile'}

