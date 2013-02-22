<%include file='../common/_header.mako' args="title=u'検索結果'"/>
<body>
    <a href="/">トップ</a> >> 「${word}」を含む公演<p/>

    <%include file='../common/_search_result.mako' args="num=num, word=word, performances=performances" />
    <hr/>

    <%include file='../common/_search.mako' args="path='/search', genre='', subgenre=''"/>
    <hr/>
    <%include file='../common/_footer.mako' />
</body>
</html>