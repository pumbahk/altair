from datetime import datetime
from ticketing.cart.resources import TicketingCartResrouce
from ticketing.core.models import DBSession
from ticketing.users.models import User, UserCredential, MemberShip, UserProfile
from .api import load_user_profile

MEMBERSHIP_NAME = '89er'

class Bj89erCartResource(TicketingCartResrouce):
    def __init__(self, request):
        super(Bj89erCartResource, self).__init__(request)
        self.event_id = request.registry.settings['89er.event_id']
        self.performance_id = request.registry.settings['89er.performance_id']

    def get_or_create_user(self):
        from ticketing.cart import api
        cart = api.get_cart(self.request)
        credential = UserCredential.query.filter(
            UserCredential.auth_identifier==str(cart.id),
        ).filter(
            UserCredential.membership_id==MemberShip.id
        ).filter(
            MemberShip.name==MEMBERSHIP_NAME
        ).first()
        if credential:
            user = credential.user
        
        else:
            user = User()

        membership = MemberShip.query.filter(MemberShip.name==MEMBERSHIP_NAME).first()
        if membership is None:
            membership = MemberShip(name=MEMBERSHIP_NAME)
            DBSession.add(membership)
        credential = user.user_credential
        if credential is None:
            credential = UserCredential(user=user, auth_identifier=str(cart.id), membership=membership)
        params = load_user_profile(self.request)
        profile = user.user_profile
        if profile is None:
            profile = UserProfile(user=user)
        profile.email=params['email']
        profile.nick_name=params['nickname']
        profile.first_name=params['first_name']
        profile.last_name=params['last_name']
        profile.first_name_kana=params['first_name_kana']
        profile.last_name_kana=params['last_name_kana']
        profile.birth_day=datetime(int(params['year']), int(params['month']), int(params['day']))
        profile.sex=params['sex']
        profile.zip=params['zipcode1'] + params['zipcode2']
        profile.prefecture=params['prefecture']
        profile.city=params['city']
        profile.street=params['address1']
        profile.address=params['address2']
        profile.other_address=None
        profile.tel_1=params['tel1_1'] + params['tel1_2'] + params['tel1_3']
        profile.tel_2=params['tel2_1'] + params['tel2_2'] + params['tel2_3']
        profile.fax=None
        DBSession.add(user)
        return user
