# -*- coding: utf-8 -*-

def add_routes(config):
    config.include('ticketing.views.admin.add_routes' , route_prefix='/admin')