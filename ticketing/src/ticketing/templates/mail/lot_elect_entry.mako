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
${h.render_payment_lots_elected_mail_viewlet(request, elected_wish.order)}

■お受取
お受取方法： ${lot_entry.payment_delivery_method_pair.delivery_method.name}
※引取手数料：${h.format_currency(lot_entry.payment_delivery_method_pair.delivery_fee)}円/${fee_type(lot_entry.payment_delivery_method_pair.delivery_method.fee_type)}をチケット代金とは別に頂戴いたします。
${h.render_delivery_lots_elected_mail_viewlet(request, elected_wish.order)}


${notice}

${footer}
