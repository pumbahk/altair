# -*- coding: utf-8 -*-


class PermissionCategory(object):
    permissions = {
        'administrator'   : u'オーガニーション管理',
        'event_viewer'    : u'公演管理閲覧',
        'event_editor'    : u'公演管理編集',
        'master_viewer'   : u'マスタ管理閲覧',
        'master_editor'   : u'マスタ管理編集',
        'sales_viewer'    : u'営業管理閲覧',
        'sales_editor'    : u'営業管理編集',
        'sales_counter'   : u'窓口業務',
        'authenticated'   : u'認証済みユーザー',
        'everybody'       : u'一般ユーザー',
        'asset_viewer'    : u'アセット閲覧',
        'asset_editor'    : u'アセット編集',
        'magazine_viewer' : u'マガジン閲覧',
        'magazine_editor' : u'マガジン編集',
        'page_viewer'     : u'ページ閲覧',
        'page_editor'     : u'ページ編集',
        'topic_viewer'    : u'トピック閲覧',
        'ticket_editor'   : u'チケット編集',
        'tag_editor'      : u'タグ編集',
        'layout_viewer'   : u'レイアウト閲覧',
        'layout_editor'   : u'レイアウト編集',
        }

    @classmethod
    def label(cls, permission):
        if isinstance(permission, list):
            retval = [cls.permissions.get(p, p) for p in permission]
            return retval
        else:
            return cls.permissions.get(permission, permission)

    @classmethod
    def all(cls):
        return cls.permissions


class RouteConfig(object):
    routes = {
        'accounts.delete'           : u'アカウント 削除',
        'accounts.edit'             : u'アカウント 編集',
        'accounts.index'            : u'アカウント 一覧',
        'accounts.new'              : u'アカウント 作成',
        'accounts.show'             : u'アカウント 詳細',
        'altair.app.ticketing.lots_admin.index' : u'',
        'altair.app.ticketing.lots_admin.search': u'',
        'api.access_token'          : u'',
        'api.forget_loggedin'       : u'',
        'api.get_frontend'          : u'',
        'api.get_seats'             : u'',
        'api.get_site_drawing'      : u'',
        'api.stock_statuses_for_event'  : u'',
        'augus.achievement.get'     : u'',
        'augus.achievement.index'   : u'',
        'augus.achievement.reserve' : u'',
        'augus.augus_venue.complete': u'',
        'augus.augus_venue.download': u'',
        'augus.augus_venue.index'   : u'',
        'augus.augus_venue.show'    : u'',
        'augus.augus_venue.upload'  : u'',
        'augus.event.show'          : u'',
        'augus.performance.edit'    : u'',
        'augus.performance.index'   : u'',
        'augus.performance.save'    : u'',
        'augus.performance.show'    : u'',
        'augus.product.edit'        : u'',
        'augus.product.index'       : u'',
        'augus.product.save'        : u'',
        'augus.product.show'        : u'',
        'augus.putback.confirm'     : u'',
        'augus.putback.index'       : u'',
        'augus.putback.new'         : u'',
        'augus.putback.reserve'     : u'',
        'augus.putback.show'        : u'',
        'augus.stock_type.edit'     : u'',
        'augus.stock_type.index'    : u'',
        'augus.stock_type.save'     : u'',
        'augus.stock_type.show'     : u'',
        'augus.test'                : u'',
        'augus.venue.download'      : u'',
        'augus.venue.index'         : u'',
        'augus.venue.upload'        : u'',
        'bookmark.edit'             : u'???',
        'bookmark.index'            : u'???',
        'bookmark.new'              : u'???',
        'cart.search'               : u'カート 検索',
        'cart.secure3d_result'      : u'',
        'cart.show'                 : u'カート 詳細',
        'cooperation.achievement'   : u'',
        'cooperation.distribution'  : u'',
        'cooperation.index'         : u'',
        'cooperation.performances'  : u'',
        'cooperation.putback'       : u'',
        'cooperation.seat_types'    : u'',
        'cooperation2.achievement'  : u'',
        'cooperation2.api.performances' : u'',
        'cooperation2.distribution' : u'',
        'cooperation2.download'     : u'',
        'cooperation2.events'       : u'',
        'cooperation2.putback'      : u'',
        'cooperation2.show'         : u'',
        'cooperation2.upload'       : u'',
        'dashboard.index'           : u'???',
        'delivery_methods.delete'   : u'引取方法 削除',
        'delivery_methods.edit'     : u'引取方法 編集',
        'delivery_methods.index'    : u'引取方法 一覧',
        'delivery_methods.new'      : u'引取方法 作成',
        'events.copy'               : u'イベント コピー',
        'events.delete'             : u'イベント 削除',
        'events.edit'               : u'イベント 編集',
        'events.index'              : u'イベント 一覧',
        'events.mailinfo.edit'      : u'',
        'events.mailinfo.index'     : u'',
        'events.new'                : u'イベント 作成',
        'events.send'               : u'',
        'events.show'               : u'イベント 詳細',
        'events.tickets.api.bundleform'     : u'',
        'events.tickets.api.ticketform'     : u'',
        'events.tickets.attributes.delete'  : u'',
        'events.tickets.attributes.edit'    : u'',
        'events.tickets.attributes.new'     : u'',
        'events.tickets.bind.ticket'        : u'',
        'events.tickets.boundtickets.data'  : u'',
        'events.tickets.boundtickets.delete': u'',
        'events.tickets.boundtickets.download'  : u'',
        'events.tickets.boundtickets.edit'  : u'',
        'events.tickets.boundtickets.index' : u'',
        'events.tickets.boundtickets.new'   : u'',
        'events.tickets.boundtickets.show'  : u'',
        'events.tickets.bundles.delete'     : u'',
        'events.tickets.bundles.edit'       : u'',
        'events.tickets.bundles.new'        : u'',
        'events.tickets.bundles.show'       : u'',
        'events.tickets.index'      : u'',
        'index'                     : u'',
        'login.access_token'        : u'',
        'login.authorize'           : u'',
        'login.client_cert'         : u'',
        'login.default'             : u'',
        'login.info'                : u'',
        'login.info.edit'           : u'',
        'login.logout'              : u'ログアウト',
        'login.missing_redirect_url': u'',
        'login.reset'               : u'',
        'login.reset.complete'      : u'',
        'lot.entries.delete_report_setting' : u'',
        'lot.entries.new_report_setting'    : u'',
        'lot.entries.send_report_setting'   : u'',
        'lots.edit'                 : u'抽選 編集',
        'lots.entries.cancel'       : u'',
        'lots.entries.cancel_electing'      : u'',
        'lots.entries.cancel_rejecting'     : u'',
        'lots.entries.close'        : u'',
        'lots.entries.elect'        : u'',
        'lots.entries.elect_all'    : u'',
        'lots.entries.elect_entry_no'       : u'',
        'lots.entries.export'       : u'',
        'lots.entries.export.html'  : u'',
        'lots.entries.import'       : u'',
        'lots.entries.index'        : u'',
        'lots.entries.reject'       : u'',
        'lots.entries.reject_entry_no'      : u'',
        'lots.entries.reject_remains'       : u'',
        'lots.entries.search'       : u'',
        'lots.entries.show'         : u'',
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
        'mailmags.subscriptions.edit'       : u'',
        'mails.preview.event'       : u'',
        'mails.preview.organization': u'',
        'mails.preview.performance'         : u'',
        'membergroups'              : u'',
        'membergroups.sales_segment_groups' : u'',
        'membergrups.api.sales_segment_groups.candidates'   : u'',
        'members.index'             : u'',
        'members.loginuser'         : u'',
        'members.member'            : u'',
        'members.membership.index'  : u'',
        'memberships'               : u'',
        'operator_roles.delete'     : u'ロール 削除',
        'operator_roles.edit'       : u'ロール 編集',
        'operator_roles.index'      : u'ロール 一覧',
        'operator_roles.new'        : u'ロール 作成',
        'operators.delete'          : u'オペレーター 削除',
        'operators.edit'            : u'オペレーター 編集',
        'operators.index'           : u'オペレーター 一覧',
        'operators.new'             : u'オペレーター 作成',
        'operators.show'            : u'オペレーター 詳細',
        'orders.api.checkbox_status': u'',
        'orders.api.edit'           : u'',
        'orders.api.edit_confirm'   : u'',
        'orders.api.get'            : u'',
        'orders.api.get.html'       : u'',
        'orders.api.orders'         : u'',
        'orders.api.performance'    : u'',
        'orders.api.performances'   : u'',
        'orders.api.sales_segment_groups'   : u'',
        'orders.api.sales_segments' : u'',
        'orders.attributes_edit'    : u'',
        'orders.cancel'             : u'予約 キャンセル',
        'orders.change_status'      : u'予約 ステータス変更',
        'orders.checked.delivered'  : u'',
        'orders.checked.queue'      : u'',
        'orders.cover.preview'      : u'',
        'orders.delete'             : u'予約 非表示',
        'orders.delivered'          : u'予約 配送済みに変更',
        'orders.download'           : u'予約 ダウンロード',
        'orders.edit.product'       : u'予約 商品情報編集',
        'orders.edit.shipping_address'  : u'予約 配送先情報編集',
        'orders.fraud.clear'        : u'',
        'orders.index'              : u'予約 一覧',
        'orders.issue_status'       : u'',
        'orders.item.preview'       : u'',
        'orders.item.preview.getdata'   : u'',
        'orders.mailinfo'           : u'',
        'orders.memo_on_order'      : u'',
        'orders.note'               : u'予約 メモ',
        'orders.print.queue'        : u'',
        'orders.print.queue.dialog' : u'',
        'orders.print.queue.each'   : u'',
        'orders.refund.checked'     : u'',
        'orders.refund.confirm'     : u'',
        'orders.refund.immediate'   : u'払戻 即時払戻',
        'orders.refund.index'       : u'払戻',
        'orders.refund.search'      : u'払戻 検索',
        'orders.reserve.complete'   : u'',
        'orders.reserve.confirm'    : u'',
        'orders.reserve.form'       : u'インナー予約',
        'orders.reserve.form.reload': u'',
        'orders.reserve.reselect'   : u'',
        'orders.sales_summary'      : u'',
        'orders.sej'                : u'',
        'orders.sej.event.refund'   : u'',
        'orders.sej.event.refund.add'   : u'',
        'orders.sej.event.refund.detail': u'',
        'orders.sej.order.cancel'   : u'',
        'orders.sej.order.info'     : u'',
        'orders.sej.order.request'  : u'',
        'orders.sej.order.ticket.data'  : u'',
        'orders.sej.order.ticket.refund': u'',
        'orders.sej.ticket_template'    : u'',
        'orders.show'               : u'予約 詳細',
        'orders.ticket.placeholder' : u'',
        'orders.undelivered'        : u'',
        'organizations.delete'      : u'オーガニゼーション 削除',
        'organizations.edit'        : u'オーガニゼーション 編集',
        'organizations.hosts.delete': u'',
        'organizations.hosts.edit'  : u'',
        'organizations.hosts.new'   : u'',
        'organizations.index'       : u'オーガニゼーション 一覧',
        'organizations.mails.new'   : u'',
        'organizations.new'         : u'オーガニゼーション 作成',
        'organizations.sej_tenant.delete'   : u'',
        'organizations.sej_tenant.edit'     : u'',
        'organizations.sej_tenant.new'      : u'',
        'organizations.settings.edit'       : u'',
        'organizations.show'        : u'',
        'payment.checkout.callback.error'   : u'',
        'payment.checkout.callback.success' : u'',
        'payment.checkout.login'    : u'',
        'payment.checkout.order_complete'   : u'',
        'payment.secure3d'          : u'',
        'payment.secure_code'       : u'',
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
        'performances.import_orders.confirm': u'',
        'performances.import_orders.delete' : u'予約インポート 削除',
        'performances.import_orders.index'  : u'予約インポート 一覧',
        'performances.import_orders.show'   : u'予約インポート 詳細',
        'performances.index'        : u'公演 一覧',
        'performances.mailinfo.edit': u'',
        'performances.mailinfo.index'       : u'',
        'performances.new'          : u'公演 作成',
        'performances.open'         : u'公演 公開/非公開',
        'performances.orion.index'  : u'',
        'performances.show'         : u'公演 詳細',
        'performances.show_tab'     : u'',
        'permissions.index'         : u'公演 一覧',
        'point_grant_settings.delete'       : u'',
        'point_grant_settings.delete_confirm'   : u'',
        'point_grant_settings.edit' : u'',
        'point_grant_settings.index': u'',
        'point_grant_settings.new'  : u'',
        'point_grant_settings.products.remove'  : u'',
        'point_grant_settings.show' : u'',
        'product.new'               : u'???',
        'product_items.delete'      : u'商品明細 削除',
        'product_items.edit'        : u'商品明細 編集',
        'product_items.new'         : u'商品明細 作成',
        'products.api.get'          : u'',
        'products.api.set'          : u'',
        'products.delete'           : u'商品 削除',
        'products.edit'             : u'商品 編集',
        'products.index'            : u'商品 一覧',
        'products.new'              : u'商品 作成',
        'qr.make'                   : u'',
        'report_settings.delete'    : u'レポート送信設定 削除',
        'report_settings.edit'      : u'レポート送信設定 編集',
        'report_settings.new'       : u'レポート送信設定 作成',
        'reports.index'             : u'',
        'reports.sales'             : u'',
        'reports.stocks'            : u'',
        'reports.stocks_by_stockholder' : u'',
        'sales_reports.event'       : u'売上レポート イベント',
        'sales_reports.index'       : u'売上レポート 一覧',
        'sales_reports.index_all'   : u'売上レポート 一覧(全期間)',
        'sales_reports.mail_body'   : u'',
        'sales_reports.performance' : u'売上レポート 公演',
        'sales_reports.preview'     : u'売上レポート プレビュー',
        'sales_reports.send_mail'   : u'売上レポート メール送信',
        'sales_segment_groups.bind_membergroup' : u'',
        'sales_segment_groups.copy' : u'販売区分グループ コピー',
        'sales_segment_groups.delete'   : u'販売区分グループ 削除',
        'sales_segment_groups.edit'     : u'販売区分グループ 編集',
        'sales_segment_groups.index'    : u'販売区分グループ 一覧',
        'sales_segment_groups.new'      : u'販売区分グループ 作成',
        'sales_segment_groups.show'     : u'販売区分グループ 詳細',
        'sales_segments.api.get_sales_segment_group_info'   : u'',
        'sales_segments.copy'       : u'販売区分 コピー',
        'sales_segments.delete'     : u'販売区分 削除',
        'sales_segments.edit'       : u'販売区分 編集',
        'sales_segments.index'      : u'販売区分 一覧',
        'sales_segments.new'        : u'販売区分 作成',
        'sales_segments.point_grant_settings.add'   : u'',
        'sales_segments.point_grant_settings.remove': u'',
        'sales_segments.show'       : u'販売区分 詳細',
        'seats.download'            : u'全座席ダウンロード',
        'service_fee_methods.delete': u'手数料 削除',
        'service_fee_methods.edit'  : u'手数料 編集',
        'service_fee_methods.index' : u'手数料 一覧',
        'service_fee_methods.new'   : u'手数料 作成',
        'service_fee_methods.system_fee_default': u'',
        'stock_holders.delete'      : u'配券先 削除',
        'stock_holders.edit'        : u'配券先 編集',
        'stock_holders.index'       : u'配券先 一覧',
        'stock_holders.new'         : u'配券先 作成',
        'stock_types.delete'        : u'席種 削除',
        'stock_types.edit'          : u'席種 編集',
        'stock_types.index'         : u'席種 一覧',
        'stock_types.new'           : u'席種 作成',
        'stocks.allocate'           : u'配席',
        'tickets.covers.delete'     : u'',
        'tickets.covers.edit'       : u'',
        'tickets.covers.new'        : u'',
        'tickets.covers.show'       : u'',
        'tickets.event.lots.mailinfo.preview'   : u'',
        'tickets.event.lots.mailinfo.send'      : u'',
        'tickets.index'             : u'',
        'tickets.pageformats.data'  : u'',
        'tickets.pageformats.delete': u'',
        'tickets.pageformats.edit'  : u'',
        'tickets.pageformats.new'   : u'',
        'tickets.pageformats.show'  : u'',
        'tickets.preview.api'       : u'',
        'tickets.preview.combobox'  : u'',
        'tickets.preview.combobox.api'  : u'',
        'tickets.preview.dialog'    : u'',
        'tickets.preview.download'  : u'',
        'tickets.preview.enqueue'   : u'',
        'tickets.preview.loadsvg.api'   : u'',
        'tickets.printer.api.dequeue'   : u'',
        'tickets.printer.api.enqueue'   : u'',
        'tickets.printer.api.formats'   : u'',
        'tickets.printer.api.history'   : u'',
        'tickets.printer.api.peek'      : u'',
        'tickets.printer.api.ticket'    : u'',
        'tickets.printer.api.ticket_data'   : u'',
        'tickets.queue.delete'      : u'',
        'tickets.queue.index'       : u'',
        'tickets.queue.mask'        : u'',
        'tickets.queue.unmask'      : u'',
        'tickets.templates.data'    : u'',
        'tickets.templates.delete'  : u'',
        'tickets.templates.download': u'',
        'tickets.templates.edit'    : u'',
        'tickets.templates.new'     : u'',
        'tickets.templates.show'    : u'',
        'tickets.templates.update_derivatives'  : u'',
        'tickets.ticketformats.data': u'',
        'tickets.ticketformats.delete'  : u'',
        'tickets.ticketformats.edit'    : u'',
        'tickets.ticketformats.new'     : u'',
        'tickets.ticketformats.show'    : u'',
        'venues.checker'            : u'',
        'venues.edit'               : u'会場 編集',
        'venues.index'              : u'会場 一覧',
        'venues.new'                : u'会場 作成',
        'venues.show'               : u'会場 詳細',
        }

    @classmethod
    def label(cls, route):
        return cls.routes.get(route, route) or route
