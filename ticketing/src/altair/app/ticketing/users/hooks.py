import logging
from altair.rakuten_auth.events import Authenticated
from pyramid.events import subscriber
from altair.app.ticketing.cart.api import get_or_create_user
from .models import UserPointAccountTypeEnum, UserPointAccountStatusEnum, UserPointAccount, UserProfile
from altair.app.ticketing.models import DBSession

logger = logging.getLogger(__name__)

@subscriber(Authenticated)
def hook(event):
    info = event.request.altair_auth_info
    logger.debug('info=%r' % info)
    user = get_or_create_user(info)
    metadata = event.metadata
    if metadata is None:
        logger.error("metadata is not provided")
        return
    if user.user_profile is None:
        user.user_profile = UserProfile()
    user.user_profile.email_1 = metadata['email_1']
    user.user_profile.nick_name = metadata['nick_name']
    user.user_profile.first_name = metadata['first_name']
    user.user_profile.last_name = metadata['last_name']
    user.user_profile.first_name_kana = metadata['first_name_kana']
    user.user_profile.last_name_kana = metadata['last_name_kana']
    user.user_profile.birthday = metadata['birthday']
    user.user_profile.sex = metadata['sex']
    user.user_profile.zip = metadata['zip']
    user.user_profile.prefecture = metadata['prefecture']
    user.user_profile.city = metadata['city']
    user.user_profile.address_1 = metadata['street']
    user.user_profile.tel_1 = metadata['tel_1']
    rakuten_point_account = metadata.get('rakuten_point_account')
    if rakuten_point_account:
        user_point_account = user.user_point_accounts.get(UserPointAccountTypeEnum.Rakuten.v)
        if user_point_account is None:
            user_point_account = UserPointAccount(user=user, type=UserPointAccountTypeEnum.Rakuten.v)
        user_point_account.account_number = rakuten_point_account
        user_point_account.status = UserPointAccountStatusEnum.Valid.v
        DBSession.add(user_point_account)
    DBSession.add(user)
