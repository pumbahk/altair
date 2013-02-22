<%include file="../common/_header.mako" args="title=u'ジャンル'"/>
<body>
    % if form.sub_genre.data == "":
        <a href="/">トップ</a> >> ${form.genre.data}
    % else:
        <a href="/">トップ</a> >> <a href="/genre?genre=${form.genre.data}">${form.genre.data}</a> >> ${form.sub_genre.data}
    % endif
<hr/>
    <%include file='../common/_attention.mako' args="attentions=attentions" />
<hr/>
    <h2>サブジャンル/カテゴリで絞り込む</h2>
    <a href="/genre?genre=${form.genre.data}&sub_genre=Jポップ・ロック">Jポップ・ロック</a>｜
    <a href="/genre?genre=${form.genre.data}&sub_genre=Jポップ・ロック">Jポップ・ロック</a>｜
    <a href="/genre?genre=${form.genre.data}&sub_genre=Jポップ・ロック">Jポップ・ロック</a>｜
    <a href="/genre?genre=${form.genre.data}&sub_genre=Jポップ・ロック">Jポップ・ロック</a>｜
    <a href="/genre?genre=${form.genre.data}&sub_genre=Jポップ・ロック">Jポップ・ロック</a>｜
<hr/>
    <%include file='../common/_topics.mako' />
<hr/>
    <%include file='../common/_area.mako' args="path='/genresearch', genre=form.genre.data, sub_genre=form.sub_genre.data" />
<hr/>
    <%include file='../common/_search.mako' args="form=form" />
<hr/>
    <%include file='../common/_hotward.mako' />
<hr/>
    <%include file="../common/_footer.mako" />
</body>
</html>
