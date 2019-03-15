# -*- coding: utf-8 -*-

from altair.app.ticketing.core.models import Event, Performance
from altair.app.ticketing.discount_code.util import get_stock_type_id_list_by_discount_code_setting_id, \
    get_choices_of_search_events, get_choices_of_search_performances
from altair.app.ticketing.events.stock_types.api import get_seat_stock_types_by_event_id
from altair.formhelpers import Translations, DateTimeFormat
from altair.formhelpers.fields import OurDateTimeField, OurSelectField
from altair.formhelpers.validators import Required, SwitchOptional
from altair.saannotation import get_annotations_for
from altair.sqlahelper import get_db_session
from pyramid.threadlocal import get_current_request
from wtforms import Form, SelectMultipleField
from wtforms import TextField, HiddenField, SelectField, BooleanField, TextAreaField, IntegerField
from wtforms.validators import Length, Optional, ValidationError, NumberRange
from .models import (
    DiscountCodeSetting,
    DiscountCodeCode,
    DiscountCodeTarget,
    CodeOrganizerEnum,
    BenefitUnitEnum,
    ConditionPriceMoreOrLessEnum,
    DiscountCodeTargetStockType)


class DiscountCodeSettingForm(Form):
    """
    「クーポン・割引コード設定 一覧」の登録フォーム（モーダル）
    """

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)
        if 'organization_id' in kwargs:
            self.organization_id = kwargs['organization_id']

    def _get_translations(self):
        return Translations()

    def _check_prefix(self):
        """
        入力された4桁の接頭辞の妥当性を確認。
        新たに登録しようとしている組み合わせが存在しないことを確認する。
        :return: エラーメッセージ
        """
        # 既存の設定の編集時（Hiddenで渡されるIDの有無で判断）
        if self.id.data:
            cnt = DiscountCodeSetting.filter_by(
                id=self.id.data,
                organization_id=self.organization_id,
                first_digit=self.first_digit.data,
                following_2to4_digits=self.following_2to4_digits.data
            ).count()
            if int(cnt) == 1:
                # 既存の設定の接頭辞を編集しなかった場合、ここでリターン
                return True

        # 新規に設定を登録する場合、あるいは編集時に別の接頭辞に変更する場合
        cnt = DiscountCodeSetting.filter_by(
            organization_id=self.organization_id,
            first_digit=self.first_digit.data,
            following_2to4_digits=self.following_2to4_digits.data
        ).count()
        if int(cnt) > 0:
            raise ValidationError(u'すでに使用されている組み合わせです')

        return True

    def _check_pair_issued_by_first_digit(self):
        first_digit = self.first_digit.data
        issued_by = self.issued_by.data
        if (first_digit == 'T' and issued_by == 'own') or (first_digit == 'E' and issued_by == 'sports_service'):
            return True
        else:
            raise ValidationError(u'コード管理元と接頭辞が正しくありません。自社(T), スポーツサービス開発(E)')

    def validate_is_valid(self, field):
        """
        クーポン・割引コード設定の有効化が可能か判定
        :param BooleanField field: フォームの入力内容
        :raise ValidationError: エラー理由
        """
        # 設定の新規作成時
        if not self.id.data:
            raise ValidationError(u'新規登録時は有効にできません。関連項目を設定後に有効にしてください。')

        # チェックが入っていた場合
        if field.data:
            err_list = []
            target_cnt = DiscountCodeTarget.filter_by(discount_code_setting_id=self.id.data).count()
            target_st_cnt = DiscountCodeTargetStockType.filter_by(discount_code_setting_id=self.id.data).count()
            if not int(target_cnt) and not int(target_st_cnt):
                err_list.append(u'適用公演、または適用席種の設定')

            if self.issued_by.data == 'own':
                code_cnt = DiscountCodeCode.filter_by(discount_code_setting_id=self.id.data).count()
                if not int(code_cnt):
                    err_list.append(u'コードの生成')

            if err_list:
                err_str = u'と'.join(err_list)
                raise ValidationError(u'{}を行うと有効に変更できます。'.format(err_str))

    def validate_first_digit(self, _):
        self._check_prefix()
        self._check_pair_issued_by_first_digit()

    def validate_following_2to4_digits(self, _):
        self._check_prefix()

    def validate_condition_price_amount(self, condition_price_amount):
        err_list = []
        if condition_price_amount.data is not None:
            priceamount = int(condition_price_amount.data)
            if priceamount < 1 or priceamount > 99999999:
                err_list.append(u'1以上の8桁の半角数字を入力してください')

        if err_list:
            err_str = u'と'.join(err_list)
            raise ValidationError(format(err_str))

    def validate_benefit_amount(self, benefit_amount):
        err_list = []
        if benefit_amount.data is not None:
            amountdata = int(benefit_amount.data)
            if self.benefit_unit.data == "%":
                if amountdata < 1 or amountdata > 100:
                    err_list.append(u'1から100までの半角数字を入力してください')
            if self.benefit_unit.data == "y":
                if amountdata < 1 or amountdata > 99999999:
                    err_list.append(u'1以上の8桁の半角数字を入力してください')

        if err_list:
            err_str = u'と'.join(err_list)
            raise ValidationError(format(err_str))

    id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )
    is_valid = BooleanField(
        label=get_annotations_for(DiscountCodeSetting.is_valid)['label'],
        default=False,
        validators=[Optional()],
    )
    name = TextField(
        label=get_annotations_for(DiscountCodeSetting.name)['label'],
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    issued_by = OurSelectField(
        label=get_annotations_for(DiscountCodeSetting.issued_by)['label'],
        default=CodeOrganizerEnum.own.v[1],
        validators=[Required()],
        choices=[code_organizer.v for code_organizer in CodeOrganizerEnum],
        coerce=str
    )
    first_digit = SelectField(
        label=get_annotations_for(DiscountCodeSetting.first_digit)['label'],
        validators=[Required()],
        choices=[
            ('T', u'T'), ('E', u'E')
        ],
        coerce=str
    )
    following_2to4_digits = TextField(
        label=get_annotations_for(DiscountCodeSetting.following_2to4_digits)['label'],
        validators=[
            Length(min=3, max=3, message=u'半角英数3文字で入力してください'),
        ]
    )
    criterion = SelectField(
        label=get_annotations_for(DiscountCodeSetting.criterion)['label'],
        validators=[Required()],
        choices=[
            ('price', u'チケット価格')
        ],
        coerce=str
    )
    condition_price_amount = IntegerField(
        label=get_annotations_for(DiscountCodeSetting.condition_price_amount)['label'],
    )
    condition_price_more_or_less = SelectField(
        label=get_annotations_for(DiscountCodeSetting.condition_price_more_or_less)['label'],
        validators=[Required()],
        choices=[condition_price_more_or_less.v for condition_price_more_or_less in ConditionPriceMoreOrLessEnum],
        coerce=str
    )
    benefit_amount = IntegerField(
        label=get_annotations_for(DiscountCodeSetting.benefit_amount)['label']
    )
    benefit_unit = SelectField(
        label=get_annotations_for(DiscountCodeSetting.benefit_unit)['label'],
        validators=[Required()],
        choices=[benefit_unit.v for benefit_unit in BenefitUnitEnum],
        coerce=str
    )
    start_at = OurDateTimeField(
        label=get_annotations_for(DiscountCodeSetting.start_at)['label'],
        validators=[SwitchOptional('end_at'),
                    Required(),
                    DateTimeFormat()],
        format='%Y-%m-%d %H:%M',
    )
    end_at = OurDateTimeField(
        label=get_annotations_for(DiscountCodeSetting.end_at)['label'],
        validators=[SwitchOptional('start_at'),
                    Required(),
                    DateTimeFormat()],
        format='%Y-%m-%d %H:%M',
    )
    explanation = TextAreaField(
        label=get_annotations_for(DiscountCodeSetting.explanation)['label'],
        validators=[Optional()],
    )
    status = HiddenField(
        label=u'状態',
    )


class DiscountCodeCodesForm(Form):
    """
    「コード一覧」の登録フォーム（モーダル）
    """

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)
        if 'organization_id' in kwargs:
            self.organization_id = kwargs['organization_id']

    id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )
    discount_code_setting_id = HiddenField(
        label=get_annotations_for(DiscountCodeCode.discount_code_setting_id)['label'],
        validators=[Optional()],
    )
    organization_id = HiddenField(
        label=get_annotations_for(DiscountCodeCode.organization_id)['label'],
        validators=[Optional()],
    )
    operator_id = HiddenField(
        label=get_annotations_for(DiscountCodeCode.operator_id)['label'],
        validators=[Optional()],
    )
    code = TextField(
        label=get_annotations_for(DiscountCodeCode.code)['label'],
        validators=[
            Optional(),
            Length(min=12, max=12, message=u'12桁で入力してください'),
        ]
    )
    order_no = TextField(
        label=u'予約番号',
    )
    used_at = OurDateTimeField(
        label=get_annotations_for(DiscountCodeCode.used_at)['label'],
        validators=[Optional(),
                    DateTimeFormat()],
        format='%Y-%m-%d %H:%M',
    )
    created_at = HiddenField(
        label=U'作成日時'
    )
    generate_num = IntegerField(
        label=u'コード生成数',
        validators=[
            NumberRange(min=0, max=50000, message=u'一度に生成できるコードの上限数は50,000です。それ以上にコードが必要な場合は複数回実行してください。')
        ]
    )


class DiscountCodeTargetForm(Form):
    """
    「適用公演」の登録フォーム（モーダル）
    """
    id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )
    discount_code_setting_id = HiddenField(
        label=get_annotations_for(DiscountCodeTarget.discount_code_setting_id)['label'],
        validators=[Optional()],
    )
    event_id = IntegerField(
        label=get_annotations_for(DiscountCodeTarget.event_id)['label'],
        default=False,
        validators=[Optional()],
    )
    performance_id = IntegerField(
        label=get_annotations_for(DiscountCodeTarget.performance_id)['label'],
        default=False,
        validators=[Optional()],
    )


class DiscountCodeTargetStForm(Form):
    """
    「適用席種」画面のフォーム
    適用実行・削除実行時の両対応
    """

    # 適用席種画面にhiddenタグで埋め込んであるform判別文字列
    FORM_REGISTER = 'register_stock_type'
    FORM_DELETE = 'delete_stock_type'

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        """
        バリデーション処理で利用される各フォームのchoices初期化
        """
        Form.__init__(self, formdata, obj, prefix, **kwargs)
        self.request = kwargs.pop('request', None)

        # 設定済の席種チェックボックスの選択オプション作成
        discount_code_setting_id = kwargs.pop('discount_code_setting_id')
        self.id.choices = get_stock_type_id_list_by_discount_code_setting_id(discount_code_setting_id)

        # POST時
        if formdata:
            # イベントの選択オプション作成
            event_id = formdata.get('event_id')
            if event_id:
                # POSTでイベントIDが指定されている場合
                event = Event.get(event_id)
                self.event_id.choices = [(event.id, event.title)]

                # 席種の選択オプション作成
                self.stock_type_id.choices = [(int(res.id), res.name) for res in
                                              get_seat_stock_types_by_event_id(event_id)]

            # 公演の選択オプション作成
            performance_id = formdata.get('performance_id')
            if performance_id:
                self.performance_id.choices = get_choices_of_search_performances(performance_id)

        # GET時
        else:
            organization_id = kwargs.pop('organization_id')
            self.event_id.choices = get_choices_of_search_events(organization_id)

    id = SelectMultipleField(
        label=get_annotations_for(DiscountCodeTargetStockType.id)['label'],
        coerce=lambda x: int(x) if x else u"",
        choices=[],
        validators=[Optional()]
    )
    discount_code_setting_id = HiddenField(
        label=get_annotations_for(DiscountCodeTargetStockType.discount_code_setting_id)['label'],
        validators=[Optional()],
    )
    event_id = SelectField(
        label=u"イベント",
        coerce=lambda x: int(x) if x else u"",
        choices=[],
        validators=[Optional()],
    )
    performance_id = SelectField(
        label=u"公演",
        coerce=lambda x: int(x) if x else u"",
        choices=[],
        validators=[Optional()],
    )
    stock_type_id = SelectMultipleField(
        label=get_annotations_for(DiscountCodeTargetStockType.performance_id)['label'],
        coerce=lambda x: int(x) if x else u"",
        choices=[],
        validators=[Optional()]
    )

    def validate_stock_type_id(self, field):
        """
        登録済みの適用席種を選択していないかチェック
        :param SelectMultipleField field: 対象席種追加でチェックの入った席種
        :return void:
        """
        session = get_db_session(get_current_request(), 'slave')
        duplicated = session.query(
            DiscountCodeTargetStockType.id,
        ).filter(
            DiscountCodeTargetStockType.stock_type_id.in_(field.data),
            DiscountCodeTargetStockType.discount_code_setting_id == int(self.data['discount_code_setting_id']),
            DiscountCodeTargetStockType.event_id == self.data['event_id'],
            DiscountCodeTargetStockType.performance_id == self.data['performance_id']
        ).order_by(
            DiscountCodeTargetStockType.id.desc()
        ).all()

        if duplicated:
            perf = session.query(Performance.name).filter_by(id=self.data['performance_id']).one()
            msg = [u'すでに「{}」に登録済みの席種が選択されています。'.format(perf.name)] + [
                u'対象席種ID: {}'.format(d.id) for d in duplicated
            ]

            raise ValidationError(' '.join(msg))


class SearchTargetForm(Form):
    """
    「適用公演」画面の検索フォーム
    """

    event_title = TextField(
        label=get_annotations_for(Event.title)['label'],
        validators=[Optional()],
        filters=[lambda x: x.strip() if x else x]  # 大文字化と左右空白のトリム
    )

    only_existing_target_event = BooleanField(
        label=u'設定済みのイベントのみ',
        default=False,
        validators=[Optional()],
    )


class SearchTargetStForm(Form):
    """
    「適用席種」画面の検索フォーム
    """

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        """
        バリデーション処理で利用される各フォームのchoices初期化
        formdataはGetDict。GETの検索パラメータが渡される
        """
        Form.__init__(self, formdata, obj, prefix, **kwargs)
        self.request = kwargs.pop('request', None)

        organization_id = kwargs.pop('organization_id')
        self.event_id.choices = get_choices_of_search_events(organization_id)

        performance_id = formdata.get('performance_id')
        if performance_id:
            # 公演の選択オプション作成
            self.performance_id.choices = get_choices_of_search_performances(performance_id)

    event_id = SelectField(
        label=u"イベント",
        coerce=lambda x: int(x) if x else u"",
        choices=[],
        validators=[Optional()],
    )

    performance_id = SelectField(
        label=u"公演",
        coerce=lambda x: int(x) if x else u"",
        choices=[],
        validators=[Optional()],
    )


class SearchCodeForm(Form):
    """
     「コード一覧」画面の検索フォーム
    """
    code = DiscountCodeCodesForm.code
