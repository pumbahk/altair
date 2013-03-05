<%include file='../common/_header.mako' args="title=u'詳細検索'"/>

<body>
<a href="/">トップ</a> >> 詳細検索<p/>

<p/>

<%include file='../detailsearch/_form.mako' args="form=form" />

<%include file='../common/_search_result.mako' args="form=form, events=events" />

<hr/>
    <%include file='../common/_footer.mako' />
</body>
</html>