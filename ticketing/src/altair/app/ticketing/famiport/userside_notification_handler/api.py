# coding: utf-8

import logging
from sqlalchemy.sql.expression import desc

__all__ = [ 
    'fetch_notifications',
    ]

logger = logging.getLogger(__name__)

def fetch_notifications(session):
    from ..userside_models import AltairFamiPortNotification
    return session.query(AltairFamiPortNotification).filter_by(reflected_at=None)
