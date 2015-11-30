import logging
from pyramid.events import subscriber
from altair.rakuten_auth.openid import RakutenOpenID
from altair.app.ticketing.security import Authenticated, reorganize_identity
from altair.app.ticketing.cart.api import get_or_create_user
from altair.app.ticketing.models import DBSession
from .models import UserPointAccountTypeEnum, UserPointAccountStatusEnum, UserPointAccount, UserProfile

logger = logging.getLogger(__name__)

@subscriber(Authenticated)
def hook(event):
    info = reorganize_identity(event.request, event.plugin, event.identity)
    info['organization_id'] = event.request.organization.id
    info['membership_source'] = event.plugin.name
    user = get_or_create_user(info)
    metadata = event.metadata
    if isinstance(event.plugin, RakutenOpenID):
        rakuten_point_account = metadata.get('rakuten_point_account')
        if rakuten_point_account:
            user_point_account = user.user_point_accounts.get(UserPointAccountTypeEnum.Rakuten.v)
            if user_point_account is None:
                user_point_account = UserPointAccount(user=user, type=UserPointAccountTypeEnum.Rakuten.v)
            user_point_account.account_number = rakuten_point_account
            user_point_account.status = UserPointAccountStatusEnum.Valid.v
            DBSession.add(user_point_account)
