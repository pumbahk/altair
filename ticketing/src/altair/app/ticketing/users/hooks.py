import logging
from altair.rakuten_auth.events import Authenticated as RakutenOpenIDAuthenticated
from altair.app.ticketing.extauth.userside_impl import Authenticated as ExtAuthAuthenticated
from altair.app.ticketing.fc_auth.events import Authenticated as FCAuthAuthenticated
from pyramid.events import subscriber
from altair.app.ticketing.cart.api import get_or_create_user
from .models import UserPointAccountTypeEnum, UserPointAccountStatusEnum, UserPointAccount, UserProfile
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.security import reorganize_identity

logger = logging.getLogger(__name__)

@subscriber(ExtAuthAuthenticated)
@subscriber(FCAuthAuthenticated)
@subscriber(RakutenOpenIDAuthenticated)
def hook(event):
    if isinstance(event, RakutenOpenIDAuthenticated):
        identity = { 'claimed_id': event.id }
    elif isinstance(event, ExtAuthAuthenticated):
        identity = event.identity
    elif isinstance(event, FCAuthAuthenticated):
        identity = event.identity
    identity = dict(identity)
    info = reorganize_identity(event.request, event.plugin, identity)
    info['organization_id'] = event.request.organization.id
    info['membership_source'] = event.plugin.name
    user = get_or_create_user(info)
    metadata = event.metadata
    if isinstance(event, RakutenOpenIDAuthenticated):
        rakuten_point_account = metadata.get('rakuten_point_account')
        if rakuten_point_account:
            user_point_account = user.user_point_accounts.get(UserPointAccountTypeEnum.Rakuten.v)
            if user_point_account is None:
                user_point_account = UserPointAccount(user=user, type=UserPointAccountTypeEnum.Rakuten.v)
            user_point_account.account_number = rakuten_point_account
            user_point_account.status = UserPointAccountStatusEnum.Valid.v
            DBSession.add(user_point_account)
