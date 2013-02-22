<%include file="../common/_header.mako" args="title=u'ジャンル'"/>
<body>
    % if subgenre is None:
        <a href="/">トップ</a> >> ${genre}
    % else:
        <a href="/">トップ</a> >> <a href="/genre?genre=${genre}">${genre}</a> >> ${subgenre}
    % endif
<hr/>
    <%include file='../common/_attention.mako' args="attentions=attentions" />
<hr/>
    <h2>サブジャンル/カテゴリで絞り込む</h2>
    <a href="/genre?genre=${genre}&subgenre=Jポップ・ロック">Jポップ・ロック</a>｜
    <a href="/genre?genre=${genre}&subgenre=Jポップ・ロック">Jポップ・ロック</a>｜
    <a href="/genre?genre=${genre}&subgenre=Jポップ・ロック">Jポップ・ロック</a>｜
    <a href="/genre?genre=${genre}&subgenre=Jポップ・ロック">Jポップ・ロック</a>｜
    <a href="/genre?genre=${genre}&subgenre=Jポップ・ロック">Jポップ・ロック</a>｜
<hr/>
    <%include file='../common/_topics.mako' />
<hr/>
    <%include file='../common/_area.mako' args="path='/genresearch', genre=genre, subgenre=subgenre" />
<hr/>
    <%include file='../common/_search.mako' args="path='/genresearch', genre=genre, subgenre=subgenre" />
<hr/>
    <%include file='../common/_hotward.mako' />
<hr/>
    <%include file="../common/_footer.mako" />
</body>
</html>
