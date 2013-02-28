<%include file='../common/_header.mako' args="title=u'検索結果'"/>
<body>
    % if form.sub_genre.data is None or form.sub_genre.data == "":
        <a href="/">トップ</a> >> <a href="/genre?genre=${form.genre.data}">${form.genre.data}</a> >> 「${form.word.data}」を含む公演
    % else:
        <a href="/">トップ</a> >> <a href="/genre?genre=${form.genre.data}">${form.genre.data}</a> >> <a href="/genre?genre=${form.genre.data}&subgenre=${form.sub_genre.data}">${form.sub_genre.data}</a> >> 「${form.word.data}」を含む公演
    % endif
    <p/>

    <%include file='../common/_search_result.mako' args="form=form, events=events" />

    <hr/>

    <%include file='../common/_search.mako' args="path='/search', genre='', subgenre=''"/>

    <hr/>
    <%include file='../common/_footer.mako' />
</body>
</html>