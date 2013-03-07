<%page args="form, events" />

<%
    num = form.num.data
    week= form.week.data
    word= form.word.data
%>

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
        % if int(form.page.data) <= 1:
            前へ
        % else:
            <a href="${form.path.data}?genre=${form.genre.data}&sub_genre=${form.sub_genre.data}&word=${form.word.data}&area=${form.area.data}&page=${int(form.page.data) - 1}">前へ</a>
        % endif

        % for count in range(int (form.page_num.data)):
            % if int(form.page.data) == count + 1:
                ${count+1}
            % else:
                <a href="${form.path.data}?genre=${form.genre.data}&sub_genre=${form.sub_genre.data}&word=${form.word.data}&area=${form.area.data}&page=${count + 1}">${count + 1}</a>
            % endif
        % endfor

        % if int(form.page.data) >= int(form.page_num.data):
            次へ
        % else:
            <a href="${form.path.data}?genre=${form.genre.data}&sub_genre=${form.sub_genre.data}&word=${form.word.data}&area=${form.area.data}&page=${int(form.page.data) + 1}">次へ</a>
        % endif
    </div>
% endif
