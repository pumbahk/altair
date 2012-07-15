# coding: utf-8

def forbidden(request):
    request.response.status = 401
    return {}

def notfound(request):
    request.response.status = 404 
    return {}
