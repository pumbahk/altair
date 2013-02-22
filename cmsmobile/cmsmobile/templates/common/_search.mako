<%page args="path, genre=None, subgenre=None" />
<%namespace file="ticketing:templates/common/helpers.html" name="h" />
チケット検索
<form action="${path}">
    <fieldset>
        <input type="hidden" name="genre" value="${genre}" />
        <input type="hidden" name="subgenre" value="${subgenre}" />
        ${h.form_item(form.word)}
        <input type="submit" value="検索"/>
    </fieldset>
</form>
<p/>