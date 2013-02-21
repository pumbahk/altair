<!DOCTYPE html>
<html>
    <%include file="../common/_header.mako" args="title=u'トップページ'"/>
    <body>
        <h2>
            <a href="/">トップ</a><p/>
        </h2>

        <%include file="../common/_search.mako" args="genre='', subgenre='', path='/search'" />
        <hr/>
        <%include file='_pickup.mako' args="promotions=promotions"/>
        <hr/>
        <%include file='_genre.mako' />
        <hr/>
        <%include file="../common/_attention.mako" />
        <hr/>
        <%include file="../common/_area.mako" args="path='/search', genre='', subgenre=''"/>
        <hr/>
        <%include file="../common/_topics.mako" args="topics=topics"/>
        <hr/>
        <%include file="../common/_hotward.mako" />

        <%include file="../common/_footer.mako" />
    </body>
</html>