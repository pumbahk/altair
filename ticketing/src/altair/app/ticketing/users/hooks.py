import logging
from altair.rakuten_auth.events import Authenticated as RakutenOpenIDAuthenticated
from altair.app.ticketing.extauth.userside_impl import Authenticated as ExtAuthAuthenticated
from altair.app.ticketing.fc_auth.events import Authenticated as FCAuthAuthenticated
from pyramid.events import subscriber
from altair.app.ticketing.cart.api import get_or_create_user
from .models import UserPointAccountTypeEnum, UserPointAccountStatusEnum, UserPointAccount, UserProfile
from altair.app.ticketing.models import DBSession

logger = logging.getLogger(__name__)

@subscriber(ExtAuthAuthenticated)
@subscriber(FCAuthAuthenticated)
@subscriber(RakutenOpenIDAuthenticated)
def hook(event):
    info = event.request.altair_auth_info
    user = get_or_create_user(info)
    metadata = event.request.altair_auth_metadata
    rakuten_point_account = metadata.get('rakuten_point_account')
    if rakuten_point_account:
        user_point_account = user.user_point_accounts.get(UserPointAccountTypeEnum.Rakuten.v)
        if user_point_account is None:
            user_point_account = UserPointAccount(user=user, type=UserPointAccountTypeEnum.Rakuten.v)
        user_point_account.account_number = rakuten_point_account
        user_point_account.status = UserPointAccountStatusEnum.Valid.v
        DBSession.add(user_point_account)
