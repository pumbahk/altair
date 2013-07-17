from altair.rakuten_auth.events import Authenticated
from pyramid.events import subscriber
from .api import get_or_create_user
from .models import UserPointAccountTypeEnum, UserPointAccountStatusEnum, UserPointAccount, UserProfile

@subscriber(Authenticated)
def hook(event):
    user = get_or_create_user(event.identity)
    identity = event.identity
    if user.user_profile is None:
        user.user_profile = UserProfile()
    user.user_profile.email_1 = identity['email_1']
    user.user_profile.nick_name = identity['nick_name']
    user.user_profile.first_name = identity['first_name']
    user.user_profile.last_name = identity['last_name']
    user.user_profile.first_name_kana = identity['first_name_kana']
    user.user_profile.last_name_kana = identity['last_name_kana']
    user.user_profile.birth_day = identity['birth_day']
    user.user_profile.sex = identity['sex']
    user.user_profile.zip = identity['zip']
    user.user_profile.prefecture = identity['prefecture']
    user.user_profile.city = identity['city']
    user.user_profile.address_1 = identity['street']
    user.user_profile.tel_1 = identity['tel_1']
    rakuten_point_account = identity.get('rakuten_point_account')
    if rakuten_point_account:
        user.user_point_accounts[UserPointAccountTypeEnum.Rakuten.v] = \
            UserPointAccount(
                type=UserPointAccountTypeEnum.Rakuten.v,
                account_number=rakuten_point_account,
                status=UserPointAccountStatusEnum.Valid.v
                )

