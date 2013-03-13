<!DOCTYPE html>
<html>
    <%include file="../common/_header.mako" args="title=u'楽天チケット'"/>
<body>

    <span style="font-size: x-small">
        % if form.sub_genre.data == "":
            <a href="/">トップ</a> >> ${form.dispgenre.data.label}
        % else:
            <a href="/">トップ</a> >> <a href="/genre?genre=${form.dispgenre.data.id}">${form.dispgenre.data.label}</a> >> ${form.dispsubgenre.data.label}
        % endif
    </span>
<hr/>
    <%include file='../common/_attention.mako' args="attentions=form.attentions.data"/>
<hr/>
    <div style="font-size: medium">サブジャンル/カテゴリで絞り込む</div>
    % for subgenre in form.genretree.data:
        <a href="/genre?genre=${form.dispgenre.data.id}&sub_genre=${subgenre.id}"><span style="font-size: x-small">${subgenre.label}</span></a>｜
    % endfor
<hr/>
    <%include file='../common/_topics.mako' args="topics=form.topics.data"/>
<hr/>
    <%include file="../common/_area.mako" args="path=form.path.data, genre=form.genre.data
                                               , sub_genre=form.sub_genre.data, num=form.num.data"/>
<hr/>
    <%include file='../common/_search.mako' args="form=form"/>
<hr/>
    <%include file='../common/_hotward.mako' args="hotwords=form.hotwords.data"/>
<hr/>
    <%include file="../common/_footer.mako"/>
</body>
</html>
