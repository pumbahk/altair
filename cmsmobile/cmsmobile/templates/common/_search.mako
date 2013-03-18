<%page args="form, genre, sub_genre" />

<form action="${form.path.data}" method="GET">
    ${form.genre}
    ${form.sub_genre}
    ${form.page}
    ${form.path}
    ${form.area}
    チケット検索
    ${form.word}<br/>
    % for error in form.word.errors:
        <font color="red">${error}</font>
    % endfor
    ${form.week_sale}今週発売のチケット<br/>
    ${form.soon_act}まもなく開演のイベント<br/>
    <input type="submit" value="検索"/><br/>
    % if genre:
        <a href="/detailsearch?genre=${genre}&sub_genre=${sub_genre}">もっと詳しく</a>
    % else:
        <a href="/detailsearch">もっと詳しく</a>
    % endif
</form>
