<%page args="word, navi_genre, navi_sub, area"/>
% if navi_sub:
    <a href="/">トップ</a> >> <a href="/genre?genre=${navi_genre.id}">${navi_genre.label}</a>
    >> <a href="/genre?genre=${navi_genre.id}&sub_genre=${navi_sub.id}">
    ${navi_sub.label}</a> >> ${area + u"で" if area else ""}「${word}」を含む公演
% else:
    <a href="/">トップ</a> >> <a href="/genre?genre=${navi_genre.id}">${navi_genre.label}</a>
    >> ${area + u"で" if area else ""}「${word}」を含む公演
% endif
