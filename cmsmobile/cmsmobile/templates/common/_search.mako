<%page args="form, genre, sub_genre" />


<div style="background-image:url(../static/bg_bar.gif);background-color:#bf0000" bgcolor="#bf0000"><font color="#ffffff" size="3"><font color="#ffbf00">■</font>チケット検索</font></div>
<div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

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
    ${form.week_sale}今週発売のチケット<br/>
    ${form.soon_act}まもなく開演のイベント<br/>
    <input type="submit" value="検索"/><br/>
    % if genre:
        <a href="/detailsearchinit?genre=${genre}&sub_genre=${sub_genre}">もっと詳しく</a>
    % else:
        <a href="/detailsearchinit">もっと詳しく</a>
    % endif
</form>
