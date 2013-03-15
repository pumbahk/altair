<%page args="event, week, month_unit, month_unit_keys, purchase_links, tickets, sales_start, sales_end" />

<div style="font-size: x-small">
公演期間：${event.deal_open.year}/${str(event.deal_open.month).zfill(2)}/${str(event.deal_open.day).zfill(2)}(${week[event.deal_open.weekday()]})-${event.deal_close.year}/${str(event.deal_close.month).zfill(2)}/${str(event.deal_close.day).zfill(2)}(${week[event.deal_close.weekday()]})
<br/>
販売期間：${sales_start.year}/${str(sales_start.month).zfill(2)}/${str(sales_start.day).zfill(2)}(${week[sales_start.weekday()]})-${sales_end.year}/${str(sales_end.month).zfill(2)}/${str(sales_end.day).zfill(2)}(${week[sales_end.weekday()]})
</div>

<div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

<div style="font-size: x-small">公演一覧へ</div>


% for count, month in enumerate(month_unit_keys):
    <a href="#${month}"><span style="font-size: x-small">${month}</span></a>
    % if count < len(month_unit_keys) - 1:
    ｜
    % endif
% endfor

<div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

<a href="#detail"><span style="font-size: x-small">公演詳細へ</span></a><br/>

<div style="background-image:url(../static/bg_bar.gif);background-color:#bf0000;font-size: medium;
                        color: #ffffff" bgcolor="#bf0000" background="../static/bg_bar.gif">公演一覧</div>

% for count, month in enumerate(month_unit_keys):
    % if count != 0:
        <hr/>
    % endif
    <a name="${month}" id="${month}"><span style="font-size: x-small">${month}</span></a><br/>
    <div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

    % for perf in event.performances:
        % if str(perf.start_on.year) + "/" + str(perf.start_on.month).zfill(2) == month:
            <a href="${purchase_links[perf.id]}">
                <span style="font-size: x-small">
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
                </span>
            </a>
        % endif
    % endfor
% endfor

<div style="background-image:url(../static/bg_bar.gif);background-color:#bf0000;font-size: medium;
                        color: #ffffff" bgcolor="#bf0000" background="../static/bg_bar.gif">公演詳細</div>

<div style="font-size: x-small">販売区分</div>
% if event.salessegment_groups:
    % for segment in event.salessegment_groups:
        <div style="font-size: x-small">
            ${segment.kind}:
            ${segment.start_on.year}/${segment.start_on.month}/${segment.start_on.day}-${segment.end_on.year}/${segment.end_on.month}/${segment.end_on.day}
        </div>
    % endfor
% endif

% if event.notice:
    <div style="font-size: x-small">詳細/注意事項</div>
    <span style="font-size: x-small">${event.notice}</span>
% endif

% if tickets:
    <div style="font-size: x-small">席種/価格</div>
    % for name in tickets.keys():
        <span style="font-size: x-small">
            ${name}:${tickets[name]}<br/>
        </span>
    % endfor
% endif

% if event.inquiry_for:
    <div style="font-size: x-small">お問合せ</div>
    <span style="font-size: x-small">
        ${event.inquiry_for}
    </span>
% endif
<%include file="../common/_footer.mako" />
