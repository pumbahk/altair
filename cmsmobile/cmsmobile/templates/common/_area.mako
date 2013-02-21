<%page args="genre" />
% if genre:
    <h1>地域から絞り込む</h1>
% else:
    <h1>地域から探す</h1>
% endif
<a href="/search?area=1">首都圏</a>｜
<a href="/search?area=2">近畿</a>｜
<a href="/search?area=3">東海</a>｜
<a href="/search?area=4">北海道</a>｜
<a href="/search?area=5">東北</a>｜
<a href="/search?area=6">北関東</a>｜
<a href="/search?area=7">甲信越</a>｜
<a href="/search?area=8">北陸</a>｜
<a href="/search?area=9">中国</a>｜
<a href="/search?area=10">四国</a>｜
<a href="/search?area=11">九州</a>｜
<a href="/search?area=12">沖縄</a>