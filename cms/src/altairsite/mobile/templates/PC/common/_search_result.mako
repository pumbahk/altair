<%page args="events, word, num, page, page_num, path, week, genre, sub_genre, area"/>
<%namespace file="../common/tags_mobile.mako" name="m" />

% if int(num):
    ${num}件見つかりました。
% else:
    % if word:
        ${word}に一致する情報は見つかりませんでした。
    % elif area:
        % if int(area) > 0:
            検索条件に一致する情報は見つかりませんでした。
        % endif
    % endif
% endif
% if events:
<%m:header>公演一覧</%m:header>
<div>
    % for count, event in enumerate(events):
<a href="/eventdetail?event_id=${event.id}&genre=${genre}&sub_genre=${sub_genre}">${event.title}</a><br/>
　販売期間：${event.deal_open.year}/${str(event.deal_open.month).zfill(2)}/${str(event.deal_open.day).zfill(2)}(${week[event.deal_open.weekday()]})〜${event.deal_close.year}/${str(event.deal_close.month).zfill(2)}/${str(event.deal_close.day).zfill(2)}(${week[event.deal_close.weekday()]})<br/>
      % if event.performances:
        % if event.performances[0].venue:
            % if not area:
                会場：${event.performances[0].venue}
            % endif
            % if count < len(events) - 1:
                <hr />
            % endif
        % endif
      % endif
    % endfor
    <div align="center">
        % if int(page) > 1:
            <a href="${path}?genre=${genre}&sub_genre=${sub_genre}&word=${word}&area=${area}&page=${int(page) - 1}">前へ</a>
        % endif

        % for count in range(int(page_num)):
            % if int(page) == count + 1:
                ${count+1}
            % else:
                <a href="${path}?genre=${genre}&sub_genre=${sub_genre}&word=${word}&area=${area}&page=${count + 1}">${count + 1}</a>
            % endif
        % endfor

        % if int(page) < int(page_num):
            <a href="${path}?genre=${genre}&sub_genre=${sub_genre}&word=${word}&area=${area}&page=${int(page) + 1}">次へ</a>
        % endif
    </div>
</div>
% endif
