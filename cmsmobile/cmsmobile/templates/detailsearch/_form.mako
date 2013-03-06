<%page args="form" />
<%namespace file="ticketing:templates/common/helpers.html" name="h" />
<form action="/detailsearch" method="POST">
    <fieldset>
        ■フリーワード検索<br/>
        <table>
            <tr>
                <td>
                    ${h.form_item(form.word)}
                </td>
                <td>
                    <input type="submit" value="検索">
                </td>
            </tr>
        </table>
        <p/>

        ■エリア
        ${h.form_item(form.area)}
        <p/>

        ■ジャンル<br/>
        ${h.form_item(form.genre)}
        <p/>
        <input type="submit" value="検索"><p/>

        ■発売状況<br/>
        ${h.form_item(form.sale)}
        <p/>

        ■販売区分<br/>
        ${h.form_item(form.sales_segment)}
        <input type="submit" value="検索"><p/>

        ■公演日で絞り込む<br/>
        <table>
            <tr>
                <td>${h.form_item(form.since_year, style="width: 60px")}</td>
                <td>年</td>
                <td>${h.form_item(form.since_month, style="width: 45px")}</td>
                <td>月</td>
                <td>${h.form_item(form.since_day, style="width: 45px")}</td>
                <td>日</td>
            </tr>
            <tr>
                <td colspan="3">
                    〜
                </td>
            </tr>
            <tr>
                <td>${h.form_item(form.year, style="width: 60px")}</td>
                <td>年</td>
                <td>${h.form_item(form.month, style="width: 45px")}</td>
                <td>月</td>
                <td>${h.form_item(form.day, style="width: 45px")}</td>
                <td>日</td>
            </tr>
        </table>
        <input type="submit" value="検索"><p/>

        <input type="hidden" name="page" value="${form.page.data}" />

    </fieldset>
</form>
