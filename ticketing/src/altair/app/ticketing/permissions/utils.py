# -*- coding: utf-8 -*-

from pyramid.interfaces import IView, IRoutesMapper, IRouteRequest, IViewClassifier, IMultiView
from zope.interface import Interface


class PermissionCategory(object):
    permissions = {
        'administrator': u'オーガニゼーション管理',
        'organization_editor': u'オーガニゼーション編集',
        'event_viewer': u'公演管理閲覧',
        'event_editor': u'公演管理編集',
        'master_viewer': u'マスタ管理閲覧',
        'master_editor': u'マスタ管理編集',
        'sales_viewer': u'営業管理閲覧',
        'sales_editor': u'営業管理編集',
        'sales_counter': u'窓口業務',
        'asset_viewer': u'アセット閲覧',
        'asset_editor': u'アセット編集',
        'magazine_viewer': u'マガジン閲覧',
        'magazine_editor': u'マガジン編集',
        'page_viewer': u'ページ閲覧',
        'page_editor': u'ページ編集',
        'topic_viewer': u'トピック閲覧',
        'ticket_editor': u'チケット編集',
        'tag_editor': u'タグ編集',
        'layout_viewer': u'レイアウト閲覧',
        'layout_editor': u'レイアウト編集',
        'member_editor': u'会員管理',
        'point_editor': u'ポイント編集',
        'venue_viewer': u'会場図閲覧',
        'reservation_editor': u'予約タブ操作',
        }

    @classmethod
    def label(cls, permission):
        if isinstance(permission, list):
            return u', '.join([cls.permissions.get(p, p) for p in permission if p is not None])
        else:
            return cls.permissions.get(permission, permission)

    @classmethod
    def all(cls):
        return cls.permissions

    @classmethod
    def items(cls):
        return sorted(cls.permissions.items(), key=lambda x: x[0])


class RouteConfig(object):
    routes = {
        'accounts.delete'           : u'アカウント 削除',
        'accounts.edit'             : u'アカウント 編集',
        'accounts.index'            : u'アカウント 一覧',
        'accounts.new'              : u'アカウント 作成',
        'accounts.show'             : u'アカウント 詳細',
        'altair.app.ticketing.lots_admin.index' : u'抽選 一覧',
        'altair.app.ticketing.lots_admin.search': u'抽選 検索',
        'api.access_token'          : None,
        'api.forget_loggedin'       : None,
        'api.get_frontend'          : None,
        'api.get_seats'             : None,
        'api.get_site_drawing'      : None,
        'api.stock_statuses_for_event'  : None,
        'augus.achievement.get'     : u'オーガス連携 販売実績取得',
        'augus.achievement.index'   : u'オーガス連携 販売実績一覧',
        'augus.achievement.reserve' : u'オーガス連携 販売実績予約',
        'augus.augus_venue.complete': None,
        'augus.augus_venue.download': u'オーガス連携 オーガス会場図ダウンロード',
        'augus.augus_venue.index'   : u'オーガス連携 オーガス会場図一覧',
        'augus.augus_venue.show'    : u'オーガス連携 オーガス会場図詳細',
        'augus.augus_venue.upload'  : u'オーガス連携 オーガス会場図アップロード',
        'augus.event.show'          : u'オーガス連携 イベント詳細',
        'augus.performance.edit'    : u'オーガス連携 公演編集',
        'augus.performance.index'   : u'オーガス連携 公演一覧',
        'augus.performance.save'    : None,
        'augus.performance.show'    : u'オーガス連携 公演詳細',
        'augus.product.edit'        : u'オーガス連携 公演編集',
        'augus.product.index'       : u'オーガス連携 公演一覧',
        'augus.product.save'        : None,
        'augus.product.show'        : u'オーガス連携 商品詳細',
        'augus.putback.confirm'     : None,
        'augus.putback.index'       : u'オーガス連携 返券一覧',
        'augus.putback.new'         : u'オーガス連携 返券作成',
        'augus.putback.reserve'     : u'オーガス連携 返券予約',
        'augus.putback.show'        : u'オーガス連携 返券詳細',
        'augus.stock_type.edit'     : u'オーガス連携 席種編集',
        'augus.stock_type.save'     : u'オーガス連携 席種保存',
        'augus.stock_type.show'     : u'オーガス連携 席種詳細',
        'augus.test'                : None,
        'augus.venue.download'      : u'オーガス連携 会場図ダウンロード',
        'augus.venue.index'         : u'オーガス連携 会場図一覧',
        'augus.venue.upload'        : u'オーガス連携 会場図アップロード',
        'cart.search'               : u'カート 検索',
        'cart.show'                 : u'カート 詳細',
        'cooperation.distribution'  : u'オーガス連携 追券',
        'cooperation.index'         : u'オーガス連携 閲覧',
        'cooperation.performances'  : u'オーガス連携 公演',
        'cooperation.putback'       : u'オーガス連携 返券',
        'cooperation.seat_types'    : u'オーガス連携 席種',
        'cooperation2.achievement'  : u'オーガス連携 販売実績',
        'cooperation2.api.performances' : None,
        'cooperation2.distribution' : u'オーガス連携 追券',
        'cooperation2.download'     : u'オーガス連携 ダウンロード',
        'cooperation2.events'       : u'オーガス連携 イベント',
        'cooperation2.putback'      : u'オーガス連携 返券',
        'cooperation2.show'         : u'オーガス連携 詳細',
        'cooperation2.upload'       : u'オーガス連携 アップロード',
        'dashboard.index'           : None,
        'delivery_methods.delete'   : u'引取方法 削除',
        'delivery_methods.edit'     : u'引取方法 編集',
        'delivery_methods.index'    : u'引取方法 一覧',
        'delivery_methods.new'      : u'引取方法 作成',
        'discount_code.settings_index': u'割引コード設定 一覧',
        'discount_code.settings_new': u'割引コード設定 作成',
        'discount_code.settings_edit': u'割引コード設定 編集',
        'discount_code.settings_delete': u'割引コード設定 削除',
        'discount_code.codes_index': u'割引コード コード一覧',
        'discount_code.codes_add': u'割引コード コード追加',
        'discount_code.codes_csv_export': u'割引コード CSV出力',
        'discount_code.codes_delete_all': u'割引コード 全コード削除',
        'discount_code.codes_used_at': u'割引コード 使用済みにする',
        'discount_code.target_index': u'割引コード 適用公演',
        'discount_code.target_confirm': u'割引コード 適用公演 変更内容確認',
        'discount_code.target_register': u'割引コード 適用公演 変更内容登録',
        'discount_code.target_st_index': u'割引コード 適用席種',
        'discount_code.report_print': u'割引コード 帳票',
        'events.copy'               : u'イベント コピー',
        'events.delete'             : u'イベント 削除',
        'events.edit'               : u'イベント 編集',
        'events.index'              : u'イベント 一覧',
        'events.mailinfo.edit'      : u'イベント メール付加情報編集',
        'events.mailinfo.index'     : u'イベント メール付加情報閲覧',
        'events.new'                : u'イベント 作成',
        'events.send'               : u'イベント CMSへ送信',
        'events.show'               : u'イベント 詳細',
        'events.tickets.api.bundleform'     : None,
        'events.tickets.api.ticketform'     : None,
        'events.tickets.attributes.delete'  : u'チケット券面構成 属性削除',
        'events.tickets.attributes.edit'    : u'チケット券面構成 属性編集',
        'events.tickets.attributes.new'     : u'チケット券面構成 属性作成',
        'events.tickets.bind.ticket'        : None,
        'events.tickets.boundtickets.data'  : None,
        'events.tickets.boundtickets.delete': u'チケット券面 削除',
        'events.tickets.boundtickets.download'  : u'チケット券面 ダウンロード',
        'events.tickets.boundtickets.edit'  : u'チケット券面 編集',
        'events.tickets.boundtickets.show'  : u'チケット券面 詳細',
        'events.tickets.bundles.delete'     : u'チケット券面構成 削除',
        'events.tickets.bundles.edit'       : u'チケット券面構成 編集',
        'events.tickets.bundles.new'        : u'チケット券面構成 作成',
        'events.tickets.bundles.show'       : u'チケット券面構成 詳細',
        'events.tickets.bundles.notify_update_ticket_info'             : u'チケット券面構成 更新をSEJ / FMに通知',
        'events.tickets.bundles.notify_update_ticket_info_error'       : u'チケット券面構成 更新をSEJ / FMに通知 エラー',
        'events.tickets.index'      : u'チケット券面 一覧',
        'index'                     : u'トップ',
        'login.access_token'        : None,
        'login.authorize'           : None,
        'login.client_cert'         : None,
        'login.default'             : None,
        'login.info'                : u'ログイン情報',
        'login.info.edit'           : u'ログイン情報 編集',
        'login.logout'              : u'ログアウト',
        'login.missing_redirect_url': None,
        'login.reset'               : u'パスワードリセット',
        'login.reset.complete'      : None,
        'lot.entries.delete_report_setting' : u'抽選レポート 設定削除',
        'lot.entries.new_report_setting'    : u'抽選レポート 設定作成',
        'lot.entries.edit_report_setting'   : u'抽選レポート 設定編集',
        'lot.entries.send_report_setting'   : u'抽選レポート 送信',
        'lots.edit'                 : u'抽選 編集',
        'lots.entries.cancel'       : u'抽選申込 キャンセル',
        'lots.entries.cancel_electing'      : u'抽選申込 当選取消',
        'lots.entries.cancel_rejecting'     : u'抽選申込 落選取消',
        'lots.entries.close'        : u'抽選申込 オーソリ解放',
        'lots.entries.elect'        : u'抽選申込 当選',
        'lots.entries.elect_all'    : None,
        'lots.entries.elect_entry_no'       : None,
        'lots.entries.stock_quantity_subtraction': u'抽選在庫　確定',
        'lots.entries.export'       : u'抽選申込 申込データエクスポート',
        'lots.entries.export.html'  : None,
        'lots.entries.import'       : u'抽選申込 当選データインポート',
        'lots.entries.index'        : u'抽選申込 一覧',
        'lots.entries.reject'       : u'抽選申込 落選',
        'lots.entries.reject_entry_no'      : None,
        'lots.entries.reject_remains'       : None,
        'lots.entries.search'       : u'抽選申込 検索',
        'lots.entries.show'         : u'抽選申込 詳細',
        'lots.entries.shipping_address.edit': u'抽選申込 配送先編集',
        'lots.index'                : u'抽選 一覧',
        'lots.new'                  : u'抽選 作成',
        'lots.product_edit'         : u'抽選商品 編集',
        'lots.product_new'          : u'抽選商品 作成',
        'lots.show'                 : u'抽選 詳細',
        'mailmags.download'         : u'メールマガジン ダウンロード',
        'mailmags.edit'             : u'メールマガジン 編集',
        'mailmags.index'            : u'メールマガジン 一覧',
        'mailmags.new'              : u'メールマガジン 作成',
        'mailmags.show'             : u'メールマガジン 詳細',
        'mailmags.subscriptions.edit'       : u'メールマガジン 購読者編集',
        'mails.preview.event'       : u'イベント メール付加情報プレビュー',
        'mails.preview.organization': u'オーガニゼーション メール付加情報プレビュー',
        'mails.preview.performance'         : u'公演 メール付加情報プレビュー',
        'membergroups'              : u'会員区分',
        'membergroups.sales_segment_groups' : u'会員区分 販売区分グループ編集',
        'membergrups.api.sales_segment_groups.candidates'   : None,
        'members.index'             : u'会員アカウント 一覧',
        'members.loginuser'         : u'会員アカウント 会員区分編集/インポート',
        'members.member'            : u'会員アカウント 会員編集',
        'members.membership.index'  : u'会員アカウント 会員一覧',
        'memberships'               : u'会員種別',
        'operator_roles.delete'     : u'ロール 削除',
        'operator_roles.edit'       : u'ロール 編集',
        'operator_roles.index'      : u'ロール 一覧',
        'operator_roles.new'        : u'ロール 作成',
        'operators.delete'          : u'オペレーター 削除',
        'operators.edit'            : u'オペレーター 編集',
        'operators.index'           : u'オペレーター 一覧',
        'operators.new'             : u'オペレーター 作成',
        'operators.show'            : u'オペレーター 詳細',
        'orders.api.checkbox_status': None,
        'orders.api.edit'           : None,
        'orders.api.edit_confirm'   : None,
        'orders.api.get'            : None,
        'orders.api.get.html'       : None,
        'orders.api.orders'         : None,
        'orders.api.performance'    : None,
        'orders.api.performances'   : None,
        'orders.api.sales_segment_groups'   : None,
        'orders.attributes_edit'    : u'予約 属性編集',
        'orders.cancel'             : u'予約 キャンセル',
        'orders.change_status'      : u'予約 ステータス変更',
        'orders.checked.delivered'  : u'予約 チェックして配送済み',
        'orders.checked.queue'      : u'予約 チェックして印刷',
        'orders.cover.preview'      : u'予約 表紙プレビュー',
        'orders.delete'             : u'予約 非表示',
        'orders.delivered'          : u'予約 配送済みに変更',
        'orders.download'           : u'予約 ダウンロード',
        'orders.edit.product'       : u'予約 商品情報編集',
        'orders.edit.shipping_address'  : u'予約 配送先情報編集',
        'orders.fraud.clear'        : u'予約 不正確認解除',
        'orders.index'              : u'予約 一覧',
        'orders.issue_status'       : u'予約 発券済みに変更',
        'orders.item.preview'       : u'予約 商品プレビュー',
        'orders.item.preview.getdata'   : None,
        'orders.mailinfo'           : u'予約 メール付加情報',
        'orders.memo_on_order'      : None,
        'orders.note'               : u'予約 メモ',
        'orders.print.queue'        : u'予約 発券',
        'orders.print.queue.dialog' : None,
        'orders.print.queue.each'   : None,
        'orders.refund.checked'     : None,
        'orders.refund.confirm'     : None,
        'orders.refund.immediate'   : u'払戻 即時払戻',
        'orders.refund.index'       : u'払戻',
        'orders.refund.search'      : u'払戻 検索',
        'orders.refund.show'        : u'払戻 払戻予約詳細',
        'orders.refund.edit'        : u'払戻 払戻予約編集',
        'orders.refund.delete'      : u'払戻 払戻予約削除',
        'orders.reserve.complete'   : None,
        'orders.reserve.confirm'    : None,
        'orders.reserve.form'       : u'インナー予約',
        'orders.reserve.form.reload': None,
        'orders.reserve.reselect'   : None,
        'orders.sales_summary'      : None,
        'orders.sej'                : None,
        'orders.sej.event.refund'   : None,
        'orders.sej.event.refund.add'   : None,
        'orders.sej.event.refund.detail': None,
        'orders.sej.order.cancel'   : None,
        'orders.sej.order.info'     : None,
        'orders.sej.order.request'  : None,
        'orders.sej.order.ticket.data'  : None,
        'orders.sej.order.ticket.refund': None,
        'orders.sej.ticket_template'    : None,
        'orders.show'               : u'予約 詳細',
        'orders.ticket.placeholder' : None,
        'orders.undelivered'        : u'予約 未配送にする',
        'organizations.delete'      : u'オーガニゼーション 削除',
        'organizations.edit'        : u'オーガニゼーション 編集',
        'organizations.hosts.delete': u'オーガニゼーション ホスト削除',
        'organizations.hosts.edit'  : u'オーガニゼーション ホスト編集',
        'organizations.hosts.new'   : u'オーガニゼーション ホスト作成',
        'organizations.index'       : u'オーガニゼーション 一覧',
        'organizations.mails.new'   : u'オーガニゼーション メール付加情報作成',
        'organizations.new'         : u'オーガニゼーション 作成',
        'organizations.sej_tenant.delete'   : u'オーガニゼーション SEJ店舗削除',
        'organizations.sej_tenant.edit'     : u'オーガニゼーション SEJ店舗編集',
        'organizations.sej_tenant.new'      : u'オーガニゼーション SEJ店舗作成',
        'organizations.settings.edit'       : u'オーガニゼーション 設定編集',
        'organizations.settings.edit.simple': u'オーガニゼーション 簡易設定編集',
        'organizations.show'        : u'オーガニゼーション 詳細',
        'payment.checkout.callback.error'   : None,
        'payment.checkout.callback.success' : None,
        'payment.checkout.login'    : None,
        'payment.checkout.order_complete'   : None,
        'payment.secure3d'          : None,
        'payment.secure3d_result'   : None,
        'payment.secure_code'       : None,
        'payment_delivery_method_pairs.delete'  : u'決済引取方法 削除',
        'payment_delivery_method_pairs.edit': u'決済引取方法 編集',
        'payment_delivery_method_pairs.new' : u'決済引取方法 作成',
        'payment_methods.delete'    : u'決済方法 削除',
        'payment_methods.edit'      : u'決済方法 編集',
        'payment_methods.index'     : u'決済方法 一覧',
        'payment_methods.new'       : u'決済方法 作成',
        'performances.copy'         : u'公演 コピー',
        'performances.delete'       : u'公演 削除',
        'performances.edit'         : u'公演 編集',
        'performances.import_orders.confirm': None,
        'performances.import_orders.delete' : u'予約インポート 削除',
        'performances.import_orders.index'  : u'予約インポート 一覧',
        'performances.import_orders.show'   : u'予約インポート 詳細',
        'performances.index'        : u'公演 一覧',
        'performances.mailinfo.edit': u'公演 メール付加情報編集',
        'performances.mailinfo.index'       : u'公演 メール付加情報一覧',
        'performances.new'          : u'公演 作成',
        'performances.open'         : u'公演 公開/非公開',
        'performances.orion.index'  : u'イベントゲート連携',
        'performances.show'         : u'公演 詳細',
        'performances.show_tab'     : None,
        'performances.discount_code_settings.show': u'割引コード設定状況',
        'performances.price_batch_update.index': u'価格一括変更',
        'performances.price_batch_update.confirm': u'価格一括変 確認',
        'performances.price_batch_update.show': u'価格一括変更 詳細',
        'performances.price_batch_update.delete': u'価格一括変更 削除',
        'performances.price_batch_update.cancel': u'価格一括変更 中止',
        'permissions.index'         : u'権限 一覧',
        'point_grant_settings.delete'       : u'ポイント付与設定 削除',
        'point_grant_settings.delete_confirm'   : None,
        'point_grant_settings.edit' : u'ポイント付与設定 編集',
        'point_grant_settings.index': u'ポイント付与設定 一覧',
        'point_grant_settings.new'  : u'ポイント付与設定 作成',
        'point_grant_settings.products.remove'  : u'ポイント付与設定 商品削除',
        'point_grant_settings.show' : u'ポイント付与設定 詳細',
        'product_items.delete'      : u'商品明細 削除',
        'product_items.edit'        : u'商品明細 編集',
        'product_items.new'         : u'商品明細 作成',
        'products.api.get'          : None,
        'products.api.set'          : None,
        'products.delete'           : u'商品 削除',
        'products.edit'             : u'商品 編集',
        'products.new'              : u'商品&商品明細 一括登録',
        'qr.make'                   : None,
        'report_settings.delete'    : u'レポート送信設定 削除',
        'report_settings.edit'      : u'レポート送信設定 編集',
        'report_settings.new'       : u'レポート送信設定 作成',
        'reports.index'             : u'帳票ダウンロード 一覧',
        'reports.sales'             : u'帳票ダウンロード 販売日程管理表',
        'reports.stocks'            : u'帳票ダウンロード 各種明細',
        'reports.stocks_by_stockholder' : u'帳票ダウンロード 各種明細(枠別)',
        'sales_reports.event'       : u'売上レポート イベント',
        'sales_reports.index'       : u'売上レポート 一覧',
        'sales_reports.mail_body'   : None,
        'sales_reports.performance' : u'売上レポート 公演',
        'sales_reports.preview'     : u'売上レポート プレビュー',
        'sales_reports.send_mail'   : u'売上レポート メール送信',
        'sales_segment_groups.bind_membergroup' : u'販売区分グループ 会員区分編集',
        'sales_segment_groups.copy' : u'販売区分グループ コピー',
        'sales_segment_groups.delete'   : u'販売区分グループ 削除',
        'sales_segment_groups.edit'     : u'販売区分グループ 編集',
        'sales_segment_groups.index'    : u'販売区分グループ 一覧',
        'sales_segment_groups.new'      : u'販売区分グループ 作成',
        'sales_segment_groups.show'     : u'販売区分グループ 詳細',
        'sales_segments.api.get_sales_segment_group_info'   : None,
        'sales_segments.copy'       : u'販売区分 コピー',
        'sales_segments.delete'     : u'販売区分 削除',
        'sales_segments.edit'       : u'販売区分 編集',
        'sales_segments.index'      : u'販売区分 一覧',
        'sales_segments.new'        : u'販売区分 作成',
        'sales_segments.point_grant_settings.add'   : u'販売区分 ポイント付与設定作成',
        'sales_segments.point_grant_settings.remove': u'販売区分 ポイント付与設定削除',
        'sales_segments.show'       : u'販売区分 詳細',
        'seats.download'            : u'全座席ダウンロード',
        'service_fee_methods.delete': u'手数料 削除',
        'service_fee_methods.edit'  : u'手数料 編集',
        'service_fee_methods.index' : u'手数料 一覧',
        'service_fee_methods.new'   : u'手数料 作成',
        'service_fee_methods.system_fee_default': None,
        'stock_holders.delete'      : u'配券先 削除',
        'stock_holders.edit'        : u'配券先 編集',
        'stock_holders.index'       : u'配券先 一覧',
        'stock_holders.new'         : u'配券先 作成',
        'stock_types.delete'        : u'席種 削除',
        'stock_types.edit'          : u'席種 編集',
        'stock_types.index'         : u'席種 一覧',
        'stock_types.new'           : u'席種 作成',
        'stocks.allocate'           : u'配席',
        'tickets.covers.delete'     : u'チケット表紙 削除',
        'tickets.covers.edit'       : u'チケット表紙 編集',
        'tickets.covers.new'        : u'チケット表紙 作成',
        'tickets.covers.show'       : u'チケット表紙 詳細',
        'tickets.event.lots.mailinfo.preview'   : u'イベント 抽選メール付加設定プレビュー',
        'tickets.event.lots.mailinfo.send'      : u'イベント 抽選メール付加設定送信',
        'tickets.index'             : u'チケット券面 一覧',
        'tickets.pageformats.data'  : None,
        'tickets.pageformats.delete': u'チケット出力形式 削除',
        'tickets.pageformats.edit'  : u'チケット出力形式 編集',
        'tickets.pageformats.new'   : u'チケット出力形式 作成',
        'tickets.pageformats.show'  : u'チケット出力形式 詳細',
        'tickets.preview.api'       : None,
        'tickets.preview.combobox'  : None,
        'tickets.preview.combobox.api'  : None,
        'tickets.preview.dialog'    : u'チケットプレビュー',
        'tickets.preview.download'  : u'チケットプレビュー ダウンロード',
        'tickets.preview.enqueue'   : None,
        'tickets.preview.loadsvg.api'   : None,
        'tickets.printer.api.dequeue'   : None,
        'tickets.printer.api.enqueue'   : None,
        'tickets.printer.api.formats'   : None,
        'tickets.printer.api.history'   : None,
        'tickets.printer.api.peek'      : None,
        'tickets.printer.api.ticket'    : None,
        'tickets.printer.api.ticket_data'   : None,
        'tickets.queue.delete'      : u'印刷キュー 削除',
        'tickets.queue.index'       : u'印刷キュー 一覧',
        'tickets.queue.mask'        : u'印刷キュー 除外',
        'tickets.queue.unmask'      : u'印刷キュー 元に戻す',
        'tickets.templates.data'    : None,
        'tickets.templates.delete'  : u'チケットテンプレート 削除',
        'tickets.templates.download': u'チケットテンプレート ダウンロード',
        'tickets.templates.edit'    : u'チケットテンプレート 編集',
        'tickets.templates.new'     : u'チケットテンプレート 作成',
        'tickets.templates.show'    : u'チケットテンプレート 詳細',
        'tickets.templates.update_derivatives'  : None,
        'tickets.ticketformats.data': None,
        'tickets.ticketformats.delete'  : u'チケット様式 削除',
        'tickets.ticketformats.edit'    : u'チケット様式 編集',
        'tickets.ticketformats.new'     : u'チケット様式 作成',
        'tickets.ticketformats.show'    : u'チケット様式 詳細',
        'venues.checker'            : u'会場 チェッカー',
        'venues.edit'               : u'会場 編集',
        'venues.index'              : u'会場 一覧',
        'venues.new'                : u'会場 作成',
        'venues.show'               : u'会場 詳細',
        }

    @classmethod
    def label(cls, route):
        return cls.routes.get(route, u'')



class IRoutePermission(Interface):
    pass


def setup_role_and_permissions(config):
    def route_permission(request):
        registry = request.registry
        route_permission = request.registry.queryUtility(IRoutePermission)

        # dict(route_name:permission)を生成
        # viewでのリンク生成時に権限有無の確認につかう
        if not route_permission:
            route_permission = {}
            mapper = registry.queryUtility(IRoutesMapper)
            if mapper:
                routes = mapper.get_routes()
                for route in routes:
                    if route.name.startswith('__'):
                        continue
                    request_iface = registry.queryUtility(IRouteRequest, name=route.name)
                    if request_iface:
                        view_callable = registry.adapters.lookup(
                            (IViewClassifier, request_iface, Interface), IView, name='', default=None
                            )
                        if IMultiView.providedBy(view_callable):
                            permissions = []
                            for order, view, phash in view_callable.get_views(request):
                                permissions.append(getattr(view, '__permission__', None))
                            permissions = list(set(permissions))
                            if len(permissions) == 1:
                                route_permission[route.name] = permissions[0]
                            else:
                                route_permission[route.name] = permissions
                        else:
                            route_permission[route.name] = getattr(view_callable, '__permission__', None)
                request.registry.registerUtility(route_permission, IRoutePermission)
        return route_permission
    config.set_request_property(route_permission, 'route_permission', reify=True)
