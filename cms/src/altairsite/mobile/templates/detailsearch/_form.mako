<%page args="form" />
<%namespace file="altairsite.mobile:templates/common/helpers.html" name="h" />

<form action="/detailsearch" method="GET">
    ■フリーワード検索<br/>
    ${form.word}
    % for error in form.word.errors:
        <br/>
        <font color="red">${error}</font>
    % endfor
    <input type="submit" value="検索">
    <div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

    ■エリア<br/>
    ${form.area}<br/><br/>

    ■ジャンル<br/>
    ${form.genre}<br/>

    <input type="submit" value="検索"/>

    <div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

    ■販売状況<br/>
    % for count, sale in enumerate(form.sale.choices):
        % if count == form.sale.data:
            <input type="radio" name="sale" value="${sale[0]}" checked="true">${sale[1]}<br/>
        % else:
            <input type="radio" name="sale" value="${sale[0]}">${sale[1]}<br/>
        % endif
    % endfor
    <br/>

    ■販売区分<br/>
    % for count, segment in enumerate(form.sales_segment.choices):
        % if count == form.sales_segment.data:
            <input type="radio" name="sales_segment" value="${segment[0]}" checked="true">${segment[1]}<br/>
        % else:
            <input type="radio" name="sales_segment" value="${segment[0]}">${segment[1]}<br/>
        % endif
    % endfor

    <input type="submit" value="検索">
    <div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

    ■公演日で絞り込む<br/>
    ${form.since_year}年${form.since_month}月${form.since_day}日〜<br/>${form.year}年${form.month}月${form.day}日
    <br/>
    % for error in form.since_year.errors:
        <font color=#FF00000>${error}</font><br/>
    % endfor
    % for error in form.year.errors:
        <font color=#FF00000>${error}</font><br/>
    % endfor
    <input type="submit" value="検索">

    ${form.page}
</form>
</span>