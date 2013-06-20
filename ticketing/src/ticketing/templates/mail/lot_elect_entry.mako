楽天チケットをご利用いただきまして、誠にありがとうございます。
%if not revised:
先日お申込みいただきました「${lot_entry.lot.name}」に関しまして、
抽選の結果、下記内容にてチケットをご用意いたしました。
%else:
先日お申込みいただきました「${lot_entry.lot.name}」に関しまして、
キャンセルが出たため、再度抽選を行い、下記内容にてチケットをご用意いたしました。
%endif

-----
%if get("name_kana").status:
■${get("name_kana").label}
${get("name_kana").body}
%endif
%if get("tel").status:
■${get("tel").label}
${get("tel").body}
%endif
%if get("mail").status:
■${get("mail").label}
${get("mail").body}
%endif

-----
%if get("order_no").status:
■${get("order_no").label}
${get("order_no").body}
%endif

%if get("order_datetime").status:
■${get("order_datetime").label}
${get("order_datetime").body}
%endif

---------------
【当選内容】
%if get("event_name").status:
■${get("event_name").label}: ${get("event_name").body}
%endif
%if get("lot_name").status:
■${get("lot_name").label}: ${get("lot_name").body}
%endif

<第${elected_wish.wish_order + 1}希望>
公演名：${elected_wish.performance.name}
公演日：${h.performance_date(elected_wish.performance)}
会場：${elected_wish.performance.venue.name}
申込内容
%for product in elected_wish.products:
${product.product.name} ${h.format_currency(product.product.price)} x ${product.quantity}枚
%endfor
チケット代金計：${h.format_currency(elected_wish.tickets_amount)}
システム利用料：${h.format_currency(elected_wish.system_fee)}円（税込）


■お支払
お支払方法： ${lot_entry.payment_delivery_method_pair.payment_method.name}
※決済手数料：${h.format_currency(lot_entry.payment_delivery_method_pair.transaction_fee)}円/${fee_type(lot_entry.payment_delivery_method_pair.payment_method.fee_type)}
${h.render_payment_lots_elected_mail_viewlet(request, lot_entry)}

■お受取
お受取方法： ${lot_entry.payment_delivery_method_pair.delivery_method.name}
※引取手数料：${h.format_currency(lot_entry.payment_delivery_method_pair.delivery_fee)}円/${fee_type(lot_entry.payment_delivery_method_pair.delivery_method.fee_type)}をチケット代金とは別に頂戴いたします。
${h.render_delivery_lots_elected_mail_viewlet(request, lot_entry)}

---------------
<注意事項>
%if lot_entry.payment_delivery_method_pair.payment_method.payment_plugin_id == plugins.MULTICHECKOUT_PAYMENT_PLUGIN_ID:
※ご当選の場合、決済期間内にご登録のクレジットカードにてお支払いとなります。
%endif
%if lot_entry.payment_delivery_method_pair.payment_method.payment_plugin_id == plugins.SEJ_PAYMENT_PLUGIN_ID:
※ご当選の場合、入金期間内にセブン-イレブン店内レジにてお支払いとなります。
%endif
%if lot_entry.payment_delivery_method_pair.delivery_method.delivery_plugin_id == plugins.SHIPPING_DELIVERY_PLUGIN_ID:
※配送でのお引取りを希望の場合には、ご登録の住所へ公演の一週間前頃までに宅配便にてお届けいたします。
%endif
%if lot_entry.payment_delivery_method_pair.delivery_method.delivery_plugin_id == plugins.SEJ_DELIVERY_PLUGIN_ID:
※【セブン-イレブン引取をご選択の場合】公演日約1週間前に、セブン-イレブン店頭レジでチケット引取をする際に必要な引換票番号をメールにてお送りいたします（本当選メールとは別のメールになります）。詳細はそちらをご確認頂き、指定発券日以降にレジにてチケットをお受取ください。
%endif

※当選チケットや当選権利の転売は禁止しております。

※お申し込み内容は、｢購入確認ページ｣( https://rt.tstar.jp/orderreview )からもご確認いただけます。
受付番号とご登録時のお電話番号をお手元にご用意のうえ、ご利用ください。

---------------
お問い合わせ
---------------
■お問い合わせ
  メール：support@ticket.rakuten.co.jp
　
■メールマガジン(楽天チケットニュース)の配信をご希望される方はこちら
　 http://emagazine.rakuten.co.jp/#17

■キャンセル・変更について
　お申し込み・購入されたチケットは、理由の如何を問わず、
　取替・変更・キャンセルはお受けできません。予めご了承ください。
　また、抽選結果についての事前お問い合わせには一切お答えいたしかねますので、
　予めご了承のほど、お願いいたします。
