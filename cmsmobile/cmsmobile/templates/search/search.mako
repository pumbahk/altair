<%include file='../common/_header.mako' args="title=u'検索結果'"/>
<body>
    <a href="/">トップ</a> >> 「${form.word.data}」を含む公演<p/>

    <%include file='../common/_search_result.mako' args="form=form, events=events" />

    <hr/>

    <%include file='../common/_search.mako' args="form=form"/>
    <hr/>
    <%include file='../common/_footer.mako' />
</body>
</html>