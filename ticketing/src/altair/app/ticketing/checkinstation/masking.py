# -*- coding:utf-8 -*-
from datetime import timedelta
from pyramid.decorator import reify
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.core.models import OrderedProductItemToken
from .models import CheckinTokenReservation

class TokenReservationFilter(object):
    expire_interval = timedelta(seconds=5*60) #期限のdefault
    def __init__(self, request, identity, token_list):
        self.request = request
        self.identity = identity
        self.token_list = token_list

    def get_partationed_reservations(self, now):
        """return [not_masked, masked] # masked is reserved by other identity"""
        token_id_list = [t.id for t in self.token_list]
        query = (OrderedProductItemToken.query
                 .filter(OrderedProductItemToken.id.in_(token_id_list))
                 .outerjoin(CheckinTokenReservation, CheckinTokenReservation.token_id==OrderedProductItemToken.id)
                 .with_entities(OrderedProductItemToken, CheckinTokenReservation))

        expire_at = now + self.expire_interval

        not_masked_reservations = []
        masked_reservations = []
        for token, reservation in query.all():
            if reservation is None:
                not_masked_reservations.append(CheckinTokenReservation(
                    token=token, 
                    identity=self.identity, 
                    expire_at=expire_at
                ))
            elif reservation.expire_at < now:
                reservation.expire_at = expire_at
                reservation.identity = self.identity
                not_masked_reservations.append(reservation)
            elif unicode(reservation.identity_id) == unicode(self.identity.id):
                not_masked_reservations.append(reservation)
            else:
                masked_reservations.append(reservation)
        ## xxx:
        DBSession.add_all(not_masked_reservations)
        return not_masked_reservations, masked_reservations

class TokenMaskPredicate(object):
    def __init__(self, not_masked_reservations, masked_reservations):
        self.not_masked_reservations = not_masked_reservations
        self.masked_reservations = masked_reservations

    @reify
    def masked_token_dict(self):
        return {unicode(r.token_id):1 for r in self.masked_reservations}

    def is_masked(self, token_id):
        return unicode(token_id) in self.masked_token_dict
