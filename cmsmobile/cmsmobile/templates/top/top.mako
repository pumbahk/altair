<!DOCTYPE html>
<html>
    <%include file="../common/_header.mako" args="title=u'トップページ'"/>
    <body>
        <%include file="../common/_search.mako" />
        <hr/>
        <%include file='_pickup.mako' />
        <hr/>
        <%include file='_genre.mako' />
        <hr/>
        <%include file="../common/_attention.mako" />
        <hr/>
        <%include file="../common/_area.mako" />
        <hr/>
        <%include file="../common/_topics.mako" />
        <hr/>
        <%include file="../common/_hotward.mako" />

        <%include file="../common/_footer.mako" />
    </body>
</html>