<%page args="path, genre, sub_genre, num" />
% if genre:
    <div style="font-size: medium">地域から絞り込む</div>
% else:
    <div style="font-size: medium">地域から探す</div>
% endif
<span style="font-size: x-small">
    <a href="${path}?genre=${genre}&sub_genre=${sub_genre}&num=${num}&page=1&area=1">首都圏</a>｜
    <a href="${path}?genre=${genre}&sub_genre=${sub_genre}&num=${num}&page=1&area=2">近畿</a>｜
    <a href="${path}?genre=${genre}&sub_genre=${sub_genre}&num=${num}&page=1&area=3">東海</a>｜
    <a href="${path}?genre=${genre}&sub_genre=${sub_genre}&num=${num}&page=1&area=4">北海道</a>｜
    <a href="${path}?genre=${genre}&sub_genre=${sub_genre}&num=${num}&page=1&area=5">東北</a>｜
    <a href="${path}?genre=${genre}&sub_genre=${sub_genre}&num=${num}&page=1&area=6">北関東</a>｜
    <a href="${path}?genre=${genre}&sub_genre=${sub_genre}&num=${num}&page=1&area=7">甲信越</a>｜
    <a href="${path}?genre=${genre}&sub_genre=${sub_genre}&num=${num}&page=1&area=8">北陸</a>｜
    <a href="${path}?genre=${genre}&sub_genre=${sub_genre}&num=${num}&page=1&area=9">中国</a>｜
    <a href="${path}?genre=${genre}&sub_genre=${sub_genre}&num=${num}&page=1&area=10">四国</a>｜
    <a href="${path}?genre=${genre}&sub_genre=${sub_genre}&num=${num}&page=1&area=11">九州</a>｜
    <a href="${path}?genre=${genre}&sub_genre=${sub_genre}&num=${num}&page=1&area=12">沖縄</a>
</span>