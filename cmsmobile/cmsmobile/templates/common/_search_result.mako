<%page args="events, word, num, page, page_num, path, week"/>

% if int(num):
    ${num}件見つかりました。
% else:
    % if word:
        <b>${word}</b>に一致する情報は見つかりませんでした。
    % endif
% endif

<h2>検索結果</h2><p/>

% if events:
    % for event in events:
        <hr/>
        <a href="/eventdetail?event_id=${event.id}">${event.title}</a><br/>
        販売：${event.deal_open.year}/${event.deal_open.month}/${event.deal_open.day}(${week[event.deal_open.weekday()]})〜${event.deal_close.year}/${event.deal_close.month}/${event.deal_close.day}(${week[event.deal_close.weekday()]})<br/>
    % endfor
% endif
<p/>

% if int(num):
    <div align="center">
        % if int(page) <= 1:
            前へ
        % else:
            <a href="${path}?genre=${genre}&sub_genre=${sub_genre}&word=${word}&area=${area}&page=${int(page) - 1}">前へ</a>
        % endif

        % for count in range(int(page_num)):
            % if int(page) == count + 1:
                ${count+1}
            % else:
                <a href="${path}?genre=${genre}&sub_genre=${sub_genre}&word=${word}&area=${area}&page=${count + 1}">${count + 1}</a>
            % endif
        % endfor

        % if int(page) >= int(page_num):
            次へ
        % else:
            <a href="${path}?genre=${genre}&sub_genre=${sub_genre}&word=${word.data}&area=${area.data}&page=${int(page) + 1}">次へ</a>
        % endif
    </div>
% endif
