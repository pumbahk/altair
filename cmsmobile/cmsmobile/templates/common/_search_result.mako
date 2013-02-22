<%page args="path, num, word, page, page_num, performances" />

% if num:
    ${num}件見つかりました。
% else:
    % if word:
        <b>${word}</b>に一致する情報は見つかりませんでした。
    % endif
% endif

<h2>検索結果</h2><p/>

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

% if num:
    <div align="center">
        % if page <= 1:
            前へ
        % else:
            <a href="${path}?word=${word}&page=${page - 1}">前へ</a>
        % endif

        % for count in range(page_num):
            % if page == count + 1:
                ${count+1}
            % else:
                <a href="${path}?word=${word}&page=${count+1}">${count+1}</a>
            % endif
        % endfor

        % if page >= page_num:
            次へ
        % else:
            <a href="${path}?word=${word}&page=${page + 1}">次へ</a>
        % endif
    </div>
% endif
