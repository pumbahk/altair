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
%if get("entry_no").status:
■${get("entry_no").label}
${get("entry_no").body}
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

${notice}

${footer}
