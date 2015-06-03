<%page args="form, genre, sub_genre" />
<%namespace file="../common/tags_mobile.mako" name="m" />
<%m:band>チケット検索</%m:band>
<%m:band bgcolor="#ffcccc" color="${None}">
<%m:line width="4" color="${None}" />
<form action="${form.path.data}" method="GET">
    ${form.genre}
    ${form.sub_genre}
    ${form.page}
    ${form.path}
    ${form.area}
    ${form.word}<br/>
    % for error in form.word.errors:
        <font color="red">${error}</font>
    % endfor
    ${form.sale}<br />
    <input type="submit" value="検索"/><br/>
    % if genre:
        <a href="/detailsearchinit?genre=${genre}&sub_genre=${sub_genre}">もっと詳しく</a>
    % else:
        <a href="/detailsearchinit">もっと詳しく</a>
    % endif
</form>
<%m:line width="4" color="${None}" />
</%m:band>
