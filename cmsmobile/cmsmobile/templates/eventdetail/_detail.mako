<%page args="event, week, month_unit, month_unit_keys, purchase_links, tickets" />

公演期間：${event.deal_open.year}/${event.deal_open.month}/${event.deal_open.day}(${week[event.deal_open.weekday()]})-${event.deal_close.year}/${event.deal_close.month}/${event.deal_close.day}(${week[event.deal_close.weekday()]})<br/>
<p/>

公演一覧へ<br/>
% for month in month_unit_keys:
    <a href="#${month}">${month}</a>｜
% endfor

<p/>
<a href="#detail">公演詳細へ</a><br/>
<hr/>
<h3>公演一覧</h3>
% for month in month_unit_keys:
    <hr/>
    <a name="${month}" id="${month}">${month}</a><br/>
    <hr/>
    % for perf in event.performances:
        % if str(perf.start_on.year) + "/" + str(perf.start_on.month) == month:
            <a href="${purchase_links[perf.id]}">
            % if perf.open_on:
                開場:${str(perf.open_on.year)[2:]}/${perf.open_on.month}/${perf.open_on.day}
            % endif
            % if perf.start_on:
                開演:${str(perf.start_on.year)[2:]}/${perf.start_on.month}/${perf.start_on.day}<br/>
            % endif
            % if perf.venue:
                会場:${perf.venue}<br/>
            % endif
        % endif
    % endfor
% endfor

<hr/>
<h3><a name="detail" id="detail">公演詳細</a></h3>
販売区分<br/>
% if event.salessegment_groups:
    % for segment in event.salessegment_groups:
        ${segment.kind}:
        ${segment.start_on.year}/${segment.start_on.month}/${segment.start_on.day}-${segment.end_on.year}/${segment.end_on.month}/${segment.end_on.day}
        <br/>
    % endfor
% endif
<p/>

% if event.description:
    詳細/注意事項<br/>
    ${event.description}
% endif
<p/>

% if tickets:
    席種/価格<br/>
    % for name in tickets.keys():
        ${name}:${tickets[name]}<br/>
    % endfor
% endif
<p/>

% if event.inquiry_for:
    お問合せ<br/>
    ${event.inquiry_for}
% endif
<%include file="../common/_footer.mako" />
