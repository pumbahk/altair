<%page args="form" />
<%namespace file="cmsmobile:templates/common/helpers.html" name="h" />

<form action="${form.path.data}" method="GET">
    <input type="hidden" name="genre" value="${form.genre.data}" />
    <input type="hidden" name="sub_genre" value="${form.sub_genre.data}" />
    <input type="hidden" name="page" value="${form.page.data}" />
    <input type="hidden" name="path" value="${form.path.data}" />
    <input type="hidden" name="area" value="${form.area.data}" />

    <span style="font-size: x-small">チケット検索</span>
    ${h.form_item(form.word, style="font-size: x-small")}
    ${h.form_item(form.week_sale, style="font-size: x-small")}
    <span style="font-size: x-small">今週発売のチケット</span>
    ${h.form_item(form.soon_act, style="font-size: x-small")}
    <span style="font-size: x-small">まもなく開演のイベント</span><br/>

    <input type="submit" value="検索" style="font-size: x-small"/><br/>
    <a href="/detailsearch"><span style="font-size: x-small">もっと詳しく</span></a>
</form>
