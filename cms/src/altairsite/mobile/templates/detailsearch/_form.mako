<%page args="form" />
<%namespace file="../common/tags_mobile.mako" name="m" />
<form action="/detailsearch" method="GET">
<%m:header>フリーワード検索</%m:header>
${form.word}<br />
% for error in form.word.errors:
<font color="red">${error}</font><br />
% endfor
<input type="submit" value="検索"><br />
<%m:header>エリア</%m:header>
${form.area}<br/>
<%m:header>ジャンル</%m:header>
${form.genre}<br/>
<input type="submit" value="検索"/><br />
<%m:header>販売状況</%m:header>
<div>
% for count, sale in enumerate(form.sale.choices):
    % if count == form.sale.data:
        <input type="radio" name="sale" value="${sale[0]}" checked="true">${sale[1]}<br/>
    % else:
        <input type="radio" name="sale" value="${sale[0]}">${sale[1]}<br/>
    % endif
% endfor
</div>
<%m:header>販売区分</%m:header>
<div>
% for count, segment in enumerate(form.sales_segment.choices):
    % if count == form.sales_segment.data:
        <input type="radio" name="sales_segment" value="${segment[0]}" checked="true">${segment[1]}<br/>
    % else:
        <input type="radio" name="sales_segment" value="${segment[0]}">${segment[1]}<br/>
    % endif
% endfor
</div>
<input type="submit" value="検索" /><br />
<%m:header>公演日で絞り込む</%m:header>
${form.since_year}年${form.since_month}月${form.since_day}日〜<br/>${form.year}年${form.month}月${form.day}日<br />
% for error in form.since_year.errors:
    <font color="#ff0000">${error}</font><br/>
% endfor
% for error in form.year.errors:
    <font color="#ff00000">${error}</font><br/>
% endfor
<input type="submit" value="検索"><br />
${form.page}
</form>
