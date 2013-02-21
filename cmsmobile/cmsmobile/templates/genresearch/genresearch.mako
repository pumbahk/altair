<%include file='../common/_header.mako' args="title=u'検索結果'"/>
<body>
    <h2>
        % if subgenre is None or subgenre == "None":
            <a href="/">トップ</a> >> <a href="/genre?genre=${genre}">${genre}</a> >> 検索
        % else:
            <a href="/">トップ</a> >> <a href="/genre?genre=${genre}">${genre}</a> >> <a href="/genre?genre=${genre}&subgenre=${subgenre}">${subgenre}</a> >> 検索
        % endif
    </h2>
    <%include file='_result.mako' args="performances=performances"/>

    <%include file='../common/_search.mako' args="path='/genresearch', genre=genre, subgenre=subgenre" />
<hr/>
    <%include file='../common/_footer.mako' />
</body>
</html>