<%page args="word, genre, sub_genre, area" />
% if sub_genre is None:
    <a href="/">トップ</a> >> <a href="/genre?genre=${genre.id}">${genre.label}</a>
        >> ${area + u"で" if area else ""}「${word}」を含む公演
% else:
    <a href="/">トップ</a> >> <a href="/genre?genre=${genre.id}">${genre.label}</a>
        >> <a href="/genre?genre=${genre.id}&sub_genre=${sub_genre.id}">
        ${sub_genre.label}</a> >> ${area + u"で" if area else ""}「${word}」を含む公演
% endif
