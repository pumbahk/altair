<%include file='../common/_header.mako' args="title=u'検索結果'"/>
<body>
    % if subgenre is None or subgenre == "None":
        <a href="/">トップ</a> >> <a href="/genre?genre=${genre}">${genre}</a> >> 「${word}」を含む公演
    % else:
        <a href="/">トップ</a> >> <a href="/genre?genre=${genre}">${genre}</a> >> <a href="/genre?genre=${genre}&subgenre=${subgenre}">${subgenre}</a> >> 「${word}」を含む公演
    % endif
    <p/>

    <%include file='../common/_search_result.mako' args="path='/genresearch', num=num, word=word, page=page, page_num=page_num, performances=performances" />
    <hr/>

    <%include file='../common/_search.mako' args="path='/search', genre='', subgenre=''"/>

    <hr/>
    <%include file='../common/_footer.mako' />
</body>
</html>