<%page args="events, word, num, page, page_num, path, week, genre, sub_genre, area, sale, sales_segment, since_year, since_month, since_day, year, month, day, errors"/> 
<%namespace file="../common/tags_mobile.mako" name="m" />
<% from altaircms.datelib import get_now %>
% if int(num):
    ${num}件見つかりました。
% else:
    % if not errors:
        % if word:
            「${word}」に一致する情報は見つかりませんでした。
        % endif
    % endif
% endif
% if events:
<%m:header>公演一覧</%m:header>
<div>
    % for count, event in enumerate(events):
<a href="/eventdetail?event_id=${event.id}&genre=${genre}&sub_genre=${sub_genre}">${event.title}</a><br />
　販売期間：${event.deal_open.year}/${str(event.deal_open.month).zfill(2)}/${str(event.deal_open.day).zfill(2)}(${week[event.deal_open.weekday()]})〜${event.deal_close.year}/${str(event.deal_close.month).zfill(2)}/${str(event.deal_close.day).zfill(2)}(${week[event.deal_close.weekday()]})<br />
      % if event.performances:
        % if event.performances[0].venue:
　会場：${event.performances[0].venue}<br />
          % if event.deal_close < get_now(request):
　<font color="red">このイベントの販売は終了しました</font><br/>
          % endif
        % endif
      % endif

      % if count < len(events):
        <hr/>
      % endif
    % endfor

    <%
        sales_segments = []
        if sales_segment:
            for segment in sales_segment:
                sales_segments.append("sales_segment=" + segment)

    %>

    % if int(page_num) > 1:
    <div align="center">
        % if int(page) > 1:
            <a href="${path}?genre=${genre}&sub_genre=${sub_genre}&word=${word}&area=${area}&sale=${sale}&${"&".join(sales_segments)}&since_year=${since_year}&since_month=${since_month}&since_day=${since_day}&year=${year}&month=${month}&day=${day}&page=${int(page) - 1}">前へ</a>
        % endif

        % for count in range(int(page_num)):
            % if int(page) == count + 1:
                ${count+1}
            % else:
                <a href="${path}?genre=${genre}&sub_genre=${sub_genre}&word=${word}&area=${area}&sale=${sale}&${"&".join(sales_segments)}&since_year=${since_year}&since_month=${since_month}&since_day=${since_day}&year=${year}&month=${month}&day=${day}&page=${count + 1}">${count + 1}</a>
            % endif
        % endfor

        % if int(page) < int(page_num):
            <a href="${path}?genre=${genre}&sub_genre=${sub_genre}&word=${word}&area=${area}&sale=${sale}&${"&".join(sales_segments)}&since_year=${since_year}&since_month=${since_month}&since_day=${since_day}&year=${year}&month=${month}&day=${day}&page=${int(page) + 1}">次へ</a>
        % endif
    </div>
    % endif
</div>
% endif
