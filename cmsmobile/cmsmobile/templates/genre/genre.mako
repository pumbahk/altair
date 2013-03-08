<!DOCTYPE html>
<html>
    <%include file="../common/_header.mako" args="title=u'ジャンル'"/>
<body>
    % if form.sub_genre.data == "":
        <a href="/">トップ</a> >> ${dispgenre.label}
    % else:
        <a href="/">トップ</a> >> <a href="/genre?genre=${dispgenre.id}">${dispgenre.label}</a> >> ${dispsubgenre.label}
    % endif
<hr/>
    <%include file='../common/_attention.mako' args="attentions=attentions"/>
<hr/>
    <h2>サブジャンル/カテゴリで絞り込む</h2>
    % for subgenre in subgenres:
        <a href="/genre?genre=${dispgenre.id}&sub_genre=${subgenre.id}">${subgenre.label}</a>｜
    % endfor
<hr/>
    <%include file='../common/_topics.mako' args="topics=topics"/>
<hr/>
    <%include file="../common/_area.mako" args="path=form.path.data, genre=form.genre.data
                                               , sub_genre=form.sub_genre.data, num=form.num.data"/>
<hr/>
    <%include file='../common/_search.mako' args="form=form"/>
<hr/>
    <%include file='../common/_hotward.mako' args="hotwords=hotwords"/>
<hr/>
    <%include file="../common/_footer.mako"/>
</body>
</html>
