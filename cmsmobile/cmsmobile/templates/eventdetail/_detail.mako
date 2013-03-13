<%page args="event, week, month_unit, month_unit_keys, purchase_links, tickets" />

<div style="font-size: x-small">
公演期間：${event.deal_open.year}/${event.deal_open.month}/${event.deal_open.day}(${week[event.deal_open.weekday()]})-${event.deal_close.year}/${event.deal_close.month}/${event.deal_close.day}(${week[event.deal_close.weekday()]})
</div>

<div style="font-size: x-small">公演一覧へ</div>


% for month in month_unit_keys:
    <a href="#${month}"><span style="font-size: x-small">${month}</span></a>｜
% endfor

<p/>
<a href="#detail"><span style="font-size: x-small">公演詳細へ</span></a><br/>

<hr/>
<span style="font-size: medium">公演一覧</span>
% for month in month_unit_keys:
    <hr/>
    <a name="${month}" id="${month}"><span style="font-size: x-small">${month}</span></a><br/>
    <hr/>
    % for perf in event.performances:
        % if str(perf.start_on.year) + "/" + str(perf.start_on.month) == month:
            <a href="${purchase_links[perf.id]}">
                <span style="font-size: x-small">
                % if perf.open_on:
                    開場:${str(perf.open_on.year)[2:]}/${perf.open_on.month}/${perf.open_on.day}
                % endif
                % if perf.start_on:
                    開演:${str(perf.start_on.year)[2:]}/${perf.start_on.month}/${perf.start_on.day}<br/>
                % endif
                % if perf.venue:
                    会場:${perf.venue}<br/>
                % endif
                </span>
            </a>
        % endif
    % endfor
% endfor

<hr/>
<a name="detail" id="detail"><span style="font-size: medium">公演詳細</span></a>
<div style="font-size: x-small">販売区分</div>
% if event.salessegment_groups:
    % for segment in event.salessegment_groups:
        <div style="font-size: x-small">
            ${segment.kind}:
            ${segment.start_on.year}/${segment.start_on.month}/${segment.start_on.day}-${segment.end_on.year}/${segment.end_on.month}/${segment.end_on.day}
        </div>
    % endfor
% endif
<p/>

% if event.description:
    <div style="font-size: x-small">詳細/注意事項</div>
    <span style="font-size: x-small">${event.description}</span>
% endif
<p/>

% if tickets:
    <div style="font-size: x-small">席種/価格</div>
    % for name in tickets.keys():
        <span style="font-size: x-small">
            ${name}:${tickets[name]}<br/>
        </span>
    % endfor
% endif
<p/>

% if event.inquiry_for:
    <div style="font-size: x-small">お問合せ</div>
    <span style="font-size: x-small">
        ${event.inquiry_for}
    </span>
% endif
<%include file="../common/_footer.mako" />
