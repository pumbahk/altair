<!DOCTYPE html>
<html>
    <%include file="../common/_header.mako" args="title=u'楽天チケット'"/>
<body>

    % if form.dispsubgenre.data:
        <div style="background-image:url(../static/bg_bar.gif);background-color:#bf0000" bgcolor="#bf0000"><font color="#ffffff" size="3"><font color="#ffc0cb">■</font>${form.dispsubgenre.data.label}</font></div>
    % else:
        <div style="background-image:url(../static/bg_bar.gif);background-color:#bf0000" bgcolor="#bf0000"><font color="#ffffff" size="3"><font color="#ffc0cb">■</font>${form.dispgenre.data.label}</font></div>
    % endif

    <div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

    <a href="/" accesskey="0">[0]戻る</a>
    <a href="/" accesskey="9">[9]トップへ</a>
    <br/><br/>

    % if form.sub_genre.data == "":
        <a href="/">トップ</a> >> ${form.dispgenre.data.label}
    % else:
        <a href="/">トップ</a> >> <a href="/genre?genre=${form.dispgenre.data.id}">${form.dispgenre.data.label}</a> >> ${form.dispsubgenre.data.label}
    % endif


    <%include file='../common/_attention.mako' args="attentions=form.attentions.data
                                          , genre=form.genre.data, sub_genre=form.sub_genre.data"/>

    <div style="background-image:url(../static/bg_bar.gif);background-color:#bf0000;
                        color: #ffffff" bgcolor="#bf0000" background="../static/bg_bar.gif">サブジャンルで絞り込む</div>

    <div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

    % for subgenre in form.genretree.data:
        <a href="/genre?genre=${form.dispgenre.data.id}&sub_genre=${subgenre.id}">${subgenre.label}</a>｜
    % endfor

    <%include file='../common/_topics.mako' args="topics=form.topics.data, genre=form.genre.data
                                                     , sub_genre=form.sub_genre.data"/>

    <%include file="../common/_area.mako" args="path=form.path.data, genre=form.genre.data
                                               , sub_genre=form.sub_genre.data, num=form.num.data"/>

    <%include file='../common/_search.mako' args="form=form, genre=form.genre.data, sub_genre=form.sub_genre.data"/>

    <%include file='../common/_hotward.mako' args="hotwords=form.hotwords.data, genre=form.genre.data, sub_genre=form.sub_genre.data"/>

    <%include file="../common/_footer.mako"/>
</body>
</html>
