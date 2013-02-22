<%include file='../common/_header.mako' args="title=u'検索結果'"/>
<body>
    % if subgenre is None or subgenre == "None":
        <a href="/">トップ</a> >> <a href="/genre?genre=${genre}">${genre}</a> >> 「${word}」を含む公演
    % else:
        <a href="/">トップ</a> >> <a href="/genre?genre=${genre}">${genre}</a> >> <a href="/genre?genre=${genre}&subgenre=${subgenre}">${subgenre}</a> >> 「${word}」を含む公演
    % endif

    <%include file='../common/_search_result.mako' args="num=num, word=word, performances=performances" />

    <hr/>
    <%include file='../common/_footer.mako' />
</body>
</html>