<%page args="word, navi_genre, navi_sub, area"/>
% if navi_sub:
    % if form.word.data:
        <a href="/">トップ</a> >> <a href="/genre?genre=${navi_genre.id}">${navi_genre.label}</a>
        >> <a href="/genre?genre=${navi_genre.id}&sub_genre=${navi_sub.id}">
        ${navi_sub.label}</a> >> 検索 ${form.navi_area.data + u"で" if form.navi_area.data else ""}「${word}」を含む公演
    % else:
        <a href="/">トップ</a> >> <a href="/genre?genre=${navi_genre.id}">${navi_genre.label}</a>
        >> <a href="/genre?genre=${navi_genre.id}&sub_genre=${navi_sub.id}">
        ${navi_sub.label}</a> >> 検索 ${u"「" + form.navi_area.data + u"」" if form.navi_area.data else ""}
    % endif
% else:
    % if form.word.data:
        <a href="/">トップ</a> >> <a href="/genre?genre=${navi_genre.id}">${navi_genre.label}</a>
        >> 検索 ${form.navi_area.data + u"で" if form.navi_area.data else ""}「${word}」を含む公演
    % else:
        <a href="/">トップ</a> >> <a href="/genre?genre=${navi_genre.id}">${navi_genre.label}</a>
        >> 検索 ${u"「" + form.navi_area.data + u"」" if form.navi_area.data else ""}
    % endif
% endif
<br/><br/>
