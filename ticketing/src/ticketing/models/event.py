# -*- coding: utf-8 -*-

from boxoffice import Client
from . import DBSession

def client_add(client):
    session = DBSession()
    session.add(client)

def client_get(client_id):
    session = DBSession()
    return session.query(Client).filter(Client.id==client_id).first()

def client_update(client):
    session = DBSession()
    session.merge(client)
    session.flush()

def client_all_list():
    session = DBSession()
    return session.query(Client).all()
