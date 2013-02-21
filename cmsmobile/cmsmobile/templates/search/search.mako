<%include file='../common/_header.mako' args="title=u'検索結果'"/>
<body>
    <h2>
        <a href="/">トップ</a> >> 検索<p/>
    </h2>

    <%include file='_result.mako' args="performances=performances"/>

    <%include file='../common/_search.mako' args="path='/search', genre='', subgenre=''"/>
<hr/>
    <%include file='../common/_footer.mako' />
</body>
</html>