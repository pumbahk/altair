<%page args="events, word, num, page, page_num, path, week, genre, sub_genre, area, mobile_tag, deal_open, deal_close"/>
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
<a href="/eventdetail?event_id=${event.id}&genre=${genre}&sub_genre=${sub_genre}">${event.title}</a><br />
% if deal_open[count] or deal_close[count]:
　販売期間：${deal_open[count]}〜${deal_close[count]}<br/>
% else:
　販売期間：販売終了<br/>
% endif
        % if event.performances[0]:
　会場：${event.performances[0].venue}<br />
            % if count < len(events) - 1:
                <hr/>
            % endif
        % endif
    % endfor


</div>
% endif

% if int(page_num) > 1:
    <div align="center">
    % if int(page) > 1:
        <a href="${request.mobile_route_path('mobile_tag_search', mobile_tag_id=mobile_tag.id, genre=genre, sub_genre=sub_genre, page=int(page) - 1)}">前へ</a>
    % endif

    % for count in range(int(page_num)):
        % if int(page) == count + 1:
            ${count+1}
        % else:
            <a href="${request.mobile_route_path('mobile_tag_search', mobile_tag_id=mobile_tag.id, genre=genre, sub_genre=sub_genre, page=count + 1)}">${count+1}</a>
        % endif
    % endfor

    % if int(page) < int(page_num):
        <a href="${request.mobile_route_path('mobile_tag_search', mobile_tag_id=mobile_tag.id, genre=genre, sub_genre=sub_genre, page=int(page) + 1)}">次へ</a>
    % endif
    </div>
% endif

