${header}
${name}　様

%if get("first_sentence").status:
${get("first_sentence").body}
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
抽選結果確認の際などに必要です。必ずお控え下さい。
%endif

%if get("order_datetime").status:
■${get("order_datetime").label}
${get("order_datetime").body}
%endif
-----
%if get("event_name").status:
■${get("event_name").label}: ${get("event_name").body}
%endif
%if get("lot_name").status:
■${get("lot_name").label}: ${get("lot_name").body}
%endif
%if get("announce_date").status:
■${get("announce_date").label}: ${get("announce_date").body}
%endif
%if get("review_url").status:
■${get("review_url").label}: ${get("review_url").body}
%endif
%for wish in lot_entry.wishes:
【第${wish.wish_order+1}希望】
公演日：${h.performance_date(wish.performance)}
会場：${wish.performance.venue.name}
申込内容
%for product in wish.products:
${product.product.name} ${h.format_currency(product.product.price)} x ${product.quantity}枚
%endfor
%if get("total_ammount").status:
${get("total_amount").label}：${h.format_currency(wish.tickets_amount)}
%endif
%if get("system_fee").status:
${get("system_fee").label}：${h.format_currency(wish.system_fee)}円（税込）
%endif
%if get("transaction_fee").status:
${get("transaction_fee").label}：${h.format_currency(wish.transaction_fee)}円
%endif
%if get("delivery_fee").status:
${get("delivery_fee").label}：${h.format_currency(wish.delivery_fee)}円
%endif
%endfor

■お支払
お支払方法： ${payment_method_name}
※決済手数料：${h.format_currency(lot_entry.payment_delivery_method_pair.transaction_fee)}円/${h.fee_type(lot_entry.payment_delivery_method_pair.payment_method.fee_type)}をチケット代金とは別に頂戴いたします。
${h.render_payment_finished_mail_viewlet(request, lot_entry)}
-----
■お受取
お受取方法： ${delivery_method_name}
※引取手数料：${h.format_currency(lot_entry.payment_delivery_method_pair.delivery_fee)}円/${h.fee_type(lot_entry.payment_delivery_method_pair.delivery_method.fee_type)}をチケット代金とは別に頂戴いたします。
${h.render_delivery_finished_mail_viewlet(request, lot_entry)}

${notice}

${footer}
