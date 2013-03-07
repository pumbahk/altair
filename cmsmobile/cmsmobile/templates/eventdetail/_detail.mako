<%page args="event, week, month_unit, month_unit_keys, purchase_links" />

公演期間：${event.deal_open.year}/${event.deal_open.month}/${event.deal_open.day}(${week[event.deal_open.weekday()]})〜${event.deal_close.year}/${event.deal_close.month}/${event.deal_close.day}(${week[event.deal_close.weekday()]})<br/>
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
    <a name="${month}">${month}</a><br/>
    <hr/>
    % for perf in event.performances:
        % if str(perf.start_on.year) + "/" + str(perf.start_on.month) == month:
                <a href="${purchase_links[perf.id]}">
            開場:${str(perf.open_on.year)[2:]}/${perf.open_on.month}/${perf.open_on.day}
            開演:${str(perf.start_on.year)[2:]}/${perf.start_on.month}/${perf.start_on.day}<br/>
            会場:${perf.venue}<br/>
        % endif
    % endfor
% endfor

<hr/>
<h3><a name="detail">公演詳細</a></h3>
販売区分<br/>
<p/>

% if event.description:
    詳細/注意事項<br/>
    ${event.description}
% endif
<p/>

席種/価格<br/>
<p/>

% if event.inquiry_for:
    お問合せ<br/>
    ${event.inquiry_for}
% endif
<%include file="../common/_footer.mako" />
