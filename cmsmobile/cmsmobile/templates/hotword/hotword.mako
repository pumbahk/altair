<!DOCTYPE html>
<html>
    <%include file='../common/_header.mako' args="title=u'楽天チケット[検索]'"/>
<body>
<a href="/">トップ

    <%include file='../common/_search_result.mako' args="form=form, events=events" />

    <hr/>
    <%include file='../common/_footer.mako' />
</body>
</html>