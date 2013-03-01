<%page args="form" />
<%namespace file="ticketing:templates/common/helpers.html" name="h" />

<form action="${form.path.data}">
    <fieldset>
        <input type="hidden" name="genre" value="${form.genre.data}" />
        <input type="hidden" name="sub_genre" value="${form.sub_genre.data}" />
        <input type="hidden" name="num" value="${form.num.data}" />
        <input type="hidden" name="page" value="${form.page.data}" />
        <input type="hidden" name="page_num" value="${form.page_num.data}" />
        <input type="hidden" name="path" value="${form.path.data}" />
        <input type="hidden" name="area" value="${form.area.data}" />
        チケット検索
        ${h.form_item(form.word)}
        <table>
            <tr>
                <td>${h.form_item(form.week_sale)}</td>
                <td>今週発売のチケット</td>
            </tr>
            <tr>
                <td>${h.form_item(form.soon_sale)}</td>
                <td>まもなく発表のイベント</td>
            </tr>
        </table>

        <input type="submit" value="検索"/>
    </fieldset>
</form>
<p/>
