<%page args="performances, num" />
% if num:
    ${num}件見つかりました。
% else:
    見つかりませんでした。
% endif

% if performances:
    % for perf in performances:
        <hr/>
        ${perf.title}<br/>
        会場：${perf.venue}<br/>
        開場：${perf.open_on}<br/>
        開始：${perf.start_on}<br/>
        終了：${perf.end_on}<br/>
        % for sale in perf.sales:
            ${sale.start_on} 〜 ${sale.end_on}<br/>
        % endfor
    % endfor
% endif
<p/>
<hr/>