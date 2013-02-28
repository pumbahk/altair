<%page args="form" />
% if genre:
    <h2>地域から絞り込む</h2>
% else:
    <h2>地域から探す</h2>
% endif
<a href="${form.path.data}?genre=${form.genre.data}&sub_genre=${form.sub_genre.data}&num=${form.num.data}&area=首都圏">首都圏</a>｜
<a href="${form.path.data}?genre=${form.genre.data}&sub_genre=${form.sub_genre.data}&num=${form.num.data}&area=近畿">近畿</a>｜
<a href="${form.path.data}?genre=${form.genre.data}&sub_genre=${form.sub_genre.data}&num=${form.num.data}&area=東海">東海</a>｜
<a href="${form.path.data}?genre=${form.genre.data}&sub_genre=${form.sub_genre.data}&num=${form.num.data}&area=北海道">北海道</a>｜
<a href="${form.path.data}?genre=${form.genre.data}&sub_genre=${form.sub_genre.data}&num=${form.num.data}&area=東方">東北</a>｜
<a href="${form.path.data}?genre=${form.genre.data}&sub_genre=${form.sub_genre.data}&num=${form.num.data}&area=北関東">北関東</a>｜
<a href="${form.path.data}?genre=${form.genre.data}&sub_genre=${form.sub_genre.data}&num=${form.num.data}&area=甲信越">甲信越</a>｜
<a href="${form.path.data}?genre=${form.genre.data}&sub_genre=${form.sub_genre.data}&num=${form.num.data}&area=北陸">北陸</a>｜
<a href="${form.path.data}?genre=${form.genre.data}&sub_genre=${form.sub_genre.data}&num=${form.num.data}&area=中国">中国</a>｜
<a href="${form.path.data}?genre=${form.genre.data}&sub_genre=${form.sub_genre.data}&num=${form.num.data}&area=四国">四国</a>｜
<a href="${form.path.data}?genre=${form.genre.data}&sub_genre=${form.sub_genre.data}&num=${form.num.data}&area=九州">九州</a>｜
<a href="${form.path.data}?genre=${form.genre.data}&sub_genre=${form.sub_genre.data}&num=${form.num.data}&area=沖縄">沖縄</a>