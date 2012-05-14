# -*- coding:utf-8 -*-

""" TBA
"""
import uuid

def cart_session_id(request):
    session = request.session
    if session.new or 'cart_id' not in session:
        session['cart_id'] = uuid.uuid4().hex

    return session['cart_id']