# coding: utf-8
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember

def remember_me(context, request, data):
    session = request.session
    username = session['username'] = request.params.get('form.username', u'')
    redirectURL = request.application_url + '/xxx'
    if 'form.remember' in request.params:
        session['remember'] = True
        headers = remember(request, username)
    return HTTPFound(location=redirectURL, headers=headers)
