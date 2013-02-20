<%page args="form" />
<%namespace file="ticketing:templates/common/helpers.html" name="h" />
チケット検索
<form action="/search" method="POST">
    <fieldset>
        ${h.form_item(form.word)}
        <input type="submit" value="検索"/>
    </fieldset>
</form>
<p/>