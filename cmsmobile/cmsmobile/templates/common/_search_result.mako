<%page args="events, word, num, page, page_num, path, week"/>

<span style="font-size: x-small">
% if int(num):
    ${num}件見つかりました。
% else:
    % if word:
        <b>${word}</b>に一致する情報は見つかりませんでした。
    % endif
% endif
</span>

<div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

<div style="background-image:url(../static/bg_bar.gif);background-color:#bf0000;font-size: medium;
                        color: #ffffff" bgcolor="#bf0000" background="../static/bg_bar.gif">検索結果</div>

% if events:
    % for count, event in enumerate(events):
        <a href="/eventdetail?event_id=${event.id}"><span style="font-size: x-small">${event.title}</span></a><br/>
        <div style="font-size: x-small">販売期間：${event.deal_open.year}/${str(event.deal_open.month).zfill(2)}/${str(event.deal_open.day).zfill(2)}(${week[event.deal_open.weekday()]})〜${event.deal_close.year}/${str(event.deal_close.month).zfill(2)}/${str(event.deal_close.day).zfill(2)}(${week[event.deal_close.weekday()]})</div>
        % if event.performances[0]:
            <div style="font-size: x-small">会場：${event.performances[0].venue}</div>

            % for group in event.salessegment_groups:
                % for segment in group.salessegments:
                    % for ticket in segment.tickets:
                        <div style="font-size: x-small">${ticket.name}：${ticket.price}</div>
                    % endfor
                % endfor
            % endfor
            % if count < len(events) - 1:
                <hr/>
            % endif
        % endif
    % endfor
% endif
<div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

% if int(num):
    <div align="center" style="font-size: x-small">
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