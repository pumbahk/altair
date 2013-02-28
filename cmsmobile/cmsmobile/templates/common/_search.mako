<%page args="form" />
<%namespace file="ticketing:templates/common/helpers.html" name="h" />
チケット検索
<form action="${form.path.data}">
    <fieldset>
        <input type="hidden" name="genre" value="${form.genre.data}" />
        <input type="hidden" name="sub_genre" value="${form.sub_genre.data}" />
        <input type="hidden" name="num" value="${form.num.data}" />
        <input type="hidden" name="page" value="${form.page.data}" />
        <input type="hidden" name="page_num" value="${form.page_num.data}" />
        <input type="hidden" name="path" value="${form.path.data}" />
        <input type="hidden" name="area" value="${form.area.data}" />
        ${h.form_item(form.word)}
        <input type="submit" value="検索"/>
    </fieldset>
</form>
<p/>
