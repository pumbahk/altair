<%include file="../common/_header.mako" args="title=u'トップページ'"/>
<body>
    <h2>
        <a href="/">トップ</a> >> ${genre}
    </h2>
<hr/>
    <%include file='../common/_attention.mako' />
<hr/>
    <%include file='../common/_topics.mako' />
<hr/>
    <%include file='../common/_area.mako' />
<hr/>
    <%include file='../common/_search.mako' />
<hr/>
    <%include file='../common/_hotward.mako' />
<hr/>
    <%include file="../common/_footer.mako" />
</body>
</html>
