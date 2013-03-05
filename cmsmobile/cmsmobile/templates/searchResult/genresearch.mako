<%include file='../common/_header.mako' args="title=u'検索結果'"/>
<body>
    % if dispsubgenre is None:
        <a href="/">トップ</a> >> <a href="/genre?genre=${dispgenre.id}">${dispgenre.label}</a>
            >> ${disparea + u"で" if disparea is not None else ""}「${form.word.data}」を含む公演
    % else:
        <a href="/">トップ</a> >> <a href="/genre?genre=${dispgenre.id}">${dispgenre.label}</a>
            >> <a href="/genre?genre=${dispgenre.id}&sub_genre=${dispsubgenre.id}">
            ${dispsubgenre.label}</a> >> ${disparea + u"で" if disparea is not None else ""}「${form.word.data}」を含む公演
    % endif
    <p/>

    <%include file='../common/_search_result.mako' args="form=form, events=events" />

    <hr/>

    <%include file='../common/_search.mako' args="path='/search', genre='', subgenre=''"/>

    <hr/>
    <%include file='../common/_footer.mako' />
</body>
</html>