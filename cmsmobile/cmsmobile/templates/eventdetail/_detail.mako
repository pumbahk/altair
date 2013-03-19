<%page args="event, week, month_unit, month_unit_keys, purchase_links, tickets, sales_start, sales_end" />

公演期間：${event.deal_open.year}/${str(event.deal_open.month).zfill(2)}/${str(event.deal_open.day).zfill(2)}(${week[event.deal_open.weekday()]})-${event.deal_close.year}/${str(event.deal_close.month).zfill(2)}/${str(event.deal_close.day).zfill(2)}(${week[event.deal_close.weekday()]})
<br/>
    % if sales_start:
        販売期間：${sales_start.year}/${str(sales_start.month).zfill(2)}/${str(sales_start.day).zfill(2)}(${week[sales_start.weekday()]})-${sales_end.year}/${str(sales_end.month).zfill(2)}/${str(sales_end.day).zfill(2)}(${week[sales_end.weekday()]})
    % endif

<div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

公演一覧へ<br/>


% for count, month in enumerate(month_unit_keys):
    <a href="#${month}">${month}</a>
    % if count < len(month_unit_keys) - 1:
    ｜
    % endif
% endfor

<div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

<a href="#detail">公演詳細へ</a><br/>

<div style="background-image:url(../static/bg_bar.gif);background-color:#bf0000" bgcolor="#bf0000"><font color="#ffffff" size="3"><font color="#ffbf00">■</font>公演一覧</font></div>

<div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

% for count, month in enumerate(month_unit_keys):
    % if count != 0:
        <hr/>
    % endif
    <a name="${month}" id="${month}">${month}</a><br/>
    <div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

    % for perf in event.performances:
        % if str(perf.start_on.year) + "/" + str(perf.start_on.month).zfill(2) == month:
            <a href="${purchase_links[perf.id]}">
                % if perf.open_on:
                    開場:${str(perf.open_on.year)[2:]}/${str(perf.open_on.month).zfill(2)}/${str(perf.open_on.day).zfill(2)}
                    ${str(perf.open_on.hour).zfill(2)}:${str(perf.open_on.minute).zfill(2)}(${week[perf.open_on.weekday()]})
                % endif
                % if perf.start_on:
                    開演:${str(perf.start_on.year)[2:]}/${str(perf.start_on.month).zfill(2)}/${str(perf.start_on.day).zfill(2)}
                    ${str(perf.start_on.hour).zfill(2)}:${str(perf.start_on.minute).zfill(2)}(${week[perf.start_on.weekday()]})<br/>
                % endif
                % if perf.venue:
                    会場:${perf.venue}<br/>
                % endif
            </a>
            <br/>
        % endif
    % endfor
% endfor

<div style="background-image:url(../static/bg_bar.gif);background-color:#bf0000" bgcolor="#bf0000"><font color="#ffffff" size="3"><font color="#ffbf00">■</font>公演詳細</font></div>

<div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

% if event.salessegment_groups:
    <div style="background-image:url(../static/bg_bar.gif);background-color:#bf0000" bgcolor="#bf0000"><font color="#ffffff" size="3"><font color="#ffff00">■</font>販売区分</font></div>
    <div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>
    % for segment in event.salessegment_groups:
        ${segment.name}:
        ${segment.start_on.year}/${segment.start_on.month}/${segment.start_on.day}-${segment.end_on.year}/${segment.end_on.month}/${segment.end_on.day}
        <br/>
    % endfor
% endif

% if event.notice:
    <div style="background-image:url(../static/bg_bar.gif);background-color:#bf0000" bgcolor="#bf0000"><font color="#ffffff" size="3"><font color="#ffff00">■</font>詳細/注意事項</font></div>
    <div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>
    ${event.notice}
% endif

<!--
% if tickets:
    席種/価格
    % for ticket in tickets:
        ${ticket.name}:${ticket.price}<br/>
    % endfor
% endif
-->

% if event.inquiry_for:
    <div style="background-image:url(../static/bg_bar.gif);background-color:#bf0000" bgcolor="#bf0000"><font color="#ffffff" size="3"><font color="#ffff00">■</font>お問い合わせ</font></div>
    <div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>
    ${event.inquiry_for}
% endif
<%include file="../common/_footer.mako" />
