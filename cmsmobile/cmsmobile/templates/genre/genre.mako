<%include file="../common/_header.mako" args="title=u'ジャンル'"/>
<body>
    <h2>
        % if subgenre is None:
            <a href="/">トップ</a> >> <a href="/genre?genre=${genre}">${genre}</a>
        % else:
            <a href="/">トップ</a> >> <a href="/genre?genre=${genre}">${genre}</a> >> <a href="/genre?genre=${genre}&subgenre=${subgenre}">${subgenre}</a>
        % endif
    </h2>
<hr/>
    <%include file='../common/_attention.mako' args="attentions=attentions" />
<hr/>
    <%include file='_subgenre.mako' args="genre=genre" />
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
