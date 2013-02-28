<%page args="form, events" />

% if int(form.num.data):
    ${form.num.data}件見つかりました。
% else:
    % if form.word.data:
        <b>${form.word.data}</b>に一致する情報は見つかりませんでした。
    % endif
% endif

<h2>検索結果</h2><p/>

% if events:
    % for event in events:
        <hr/>
        <a href="/detail?event_id=${event.id}">${event.title}</a><br/>
        販売：${event.deal_open}〜${event.deal_close}<br/>
    % endfor
% endif
<p/>

% if int(form.num.data):
    <div align="center">
        % if int(form.page.data) <= 1:
            前へ
        % else:
            <a href="${form.path.data}?genre=${form.genre.data}&sub_genre=${form.sub_genre.data}&word=${form.word.data}&page=${int(form.page.data) - 1}">前へ</a>
        % endif

        % for count in range(int (form.page_num.data)):
            % if int(form.page.data) == count + 1:
                ${count+1}
            % else:
                <a href="${form.path.data}?genre=${form.genre.data}&sub_genre=${form.sub_genre.data}&word=${form.word.data}&page=${count + 1}">${count + 1}</a>
            % endif
        % endfor

        % if int(form.page.data) >= int(form.page_num.data):
            次へ
        % else:
            <a href="${form.path.data}?genre=${form.genre.data}&sub_genre=${form.sub_genre.data}&word=${form.word.data}&page=${int(form.page.data) + 1}">次へ</a>
        % endif
    </div>
% endif
