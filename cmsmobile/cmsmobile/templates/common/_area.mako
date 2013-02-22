<%page args="path, genre=None, sub_genre=None" />
% if genre:
    <h2>地域から絞り込む</h2>
% else:
    <h2>地域から探す</h2>
% endif
<a href="${path}?genre=${genre}&sub_genre=${sub_genre}&area=1">首都圏</a>｜
<a href="${path}?genre=${genre}&sub_genre=${sub_genre}&area=2">近畿</a>｜
<a href="${path}?genre=${genre}&sub_genre=${sub_genre}&area=3">東海</a>｜
<a href="${path}?genre=${genre}&sub_genre=${sub_genre}&area=4">北海道</a>｜
<a href="${path}?genre=${genre}&sub_genre=${sub_genre}&area=5">東北</a>｜
<a href="${path}?genre=${genre}&sub_genre=${sub_genre}&area=6">北関東</a>｜
<a href="${path}?genre=${genre}&sub_genre=${sub_genre}&area=7">甲信越</a>｜
<a href="${path}?genre=${genre}&sub_genre=${sub_genre}&area=8">北陸</a>｜
<a href="${path}?genre=${genre}&sub_genre=${sub_genre}&area=9">中国</a>｜
<a href="${path}?genre=${genre}&sub_genre=${sub_genre}&area=10">四国</a>｜
<a href="${path}?genre=${genre}&sub_genre=${sub_genre}&area=11">九州</a>｜
<a href="${path}?genre=${genre}&sub_genre=${sub_genre}&area=12">沖縄</a>