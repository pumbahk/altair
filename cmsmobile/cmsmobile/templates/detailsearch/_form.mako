<%page args="form" />
<%namespace file="cmsmobile:templates/common/helpers.html" name="h" />

<form action="/detailsearch" method="POST">
    <fieldset>
        <div style="font-size: x-small">■フリーワード検索<div/>
        ${h.form_item(form.word, style="font-size: x-small")}
        <input type="submit" value="検索" style="font-size: x-small"><br/>

        <span style="font-size: x-small">■エリア</span>
        ${h.form_item(form.area, style="font-size: x-small")}

        <span style="font-size: x-small">■ジャンル<span/>
        ${h.form_item(form.genre, style="font-size: x-small")}

        <input type="submit" value="検索" style="font-size: x-small">

        <div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

        <span style="font-size: x-small">■発売状況<span/>
        ${h.form_item(form.sale, style="font-size: x-small")}

        <span style="font-size: x-small">■販売区分<span/>
        ${h.form_item(form.sales_segment, style="font-size: x-small")}

        <input type="submit" value="検索" style="font-size: x-small">
        <div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

        <span style="font-size: x-small">■公演日で絞り込む<span/>
        ${h.form_item(form.since_year, style="width: 60px, font-size: x-small")}
        <span style="font-size: x-small">年</span>
        ${h.form_item(form.since_month, style="width: 45px, font-size: x-small")}
        <span style="font-size: x-small">月</span>
        ${h.form_item(form.since_day, style="width: 45px, font-size: x-small")}
        <span style="font-size: x-small">日</span><
        <span style="font-size: x-small">〜</span>
        ${h.form_item(form.year, style="width: 60px, font-size: x-small")}
        <span style="font-size: x-small">年</span>
        ${h.form_item(form.month, style="width: 45px, font-size: x-small")}
        <span style="font-size: x-small">月</span>
        ${h.form_item(form.day, style="width: 45px, font-size: x-small")}
        <span style="font-size: x-small">日</span>
        <input type="submit" value="検索" style="font-size: x-small">

        <input type="hidden" name="page" value="${form.page.data}" />

    </fieldset>
</form>
</span>