# encoding: utf-8

from altair.app.ticketing.users.models import UserPointAccountTypeEnum
from markupsafe import Markup
from .models import PointGrantStatusEnum

point_types = {
    UserPointAccountTypeEnum.Rakuten.v: u'楽天スーパーポイント'
    }

grant_statuses = {
    PointGrantStatusEnum.InvalidRecord.v:              u'レコードが不正',
    PointGrantStatusEnum.InvalidPointAccountNumber.v:  u'ポイント口座番号が不正',
    PointGrantStatusEnum.InvalidReasonCode.v:          u'事由コードが不正',
    PointGrantStatusEnum.InvalidReferenceKey.v:        u'参照キー (受付番号) が不正',
    PointGrantStatusEnum.InvalidSubKey.v:              u'サブキーが不正',
    PointGrantStatusEnum.InvalidPointValue.v:          u'付与ポイント数が不正',
    PointGrantStatusEnum.InvalidShopName.v:            u'店舗名が不正',
    PointGrantStatusEnum.NoSuchPointAccount.v:         u'ポイント口座該当なし',
    PointGrantStatusEnum.NoSuchReasonCode.v:           u'事由コード該当なし',
    PointGrantStatusEnum.KeyAlreadyExists.v:           u'同じ参照キーとサブキーの組み合わせで付与済み',
    }

def format_point_type(type_value):
    retval = None
    try:
        retval = point_types.get(int(type_value))
    except (TypeError, ValueError):
        pass
    return retval or u'-'

def format_grant_status(grant_status_value):
    if grant_status_value is None:
        return Markup(u'-')
    elif grant_status_value == '':
        return Markup(u'済')
    else:
        s = grant_statuses.get(grant_status_value)
        if s:
            return Markup(u'<span class="error">%s (%s)</span>' % (s, grant_status_value))
        else:
            return Markup(u'<span class="error">不明なステータスコード (%s)</span>' % (grant_status_value))
