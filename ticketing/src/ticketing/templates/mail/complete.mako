${header}
${name}　様


以下のご注文の受付が完了しました。ご利用ありがとうございました。

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
予約内容確認の際などに必要です。必ずお控え下さい。
%endif

%if get("order_datetime").status:
■${get("order_datetime").label}
${get("order_datetime").body}
%endif
-----
%if get("event_name").status:
${get("event_name").body}
%endif
%if get("pdate").status:
${get("pdate").label}: ${get("pdate").body}(予定)
%endif
%if get("venue").status:
${get("venue").label}: ${get("venue").body}
%endif

%if get("for_seat").status:
■${get("for_seat").label}
${get("for_seat").body}
%endif

%if get("for_product").status:
■${get("for_product").label}
${get("for_product").body}
%endif

■サービス利用料・手数料
%if get("system_fee").status:
${get("system_fee").label}: ${get("system_fee").body}
%endif
%if get("transaction_fee").status:
${get("transaction_fee").label}: ${get("transaction_fee").body}
%endif
%if get("delivery_fee").status:
${get("delivery_fee").label}: ${get("delivery_fee").body}
%endif

%if get("total_amount").status:
■${get("total_amount").label}
${get("total_amount").body}
%endif

-----
■お支払
お支払方法： ${payment_method_name}
${h.render_payment_finished_mail_viewlet(request, order)}
-----
■お受取
お受取方法： ${delivery_method_name}
${h.render_delivery_finished_mail_viewlet(request, order)}

${notice}

※本メールは自動配信メールとなり、こちらに返信されても返答はいたしかねます。

※営利目的としたチケットの転売は禁止となっております。

${footer}
