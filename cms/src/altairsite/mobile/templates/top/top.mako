<!DOCTYPE html>
<html>
    <%include file="../common/_header.mako" args="title=u'楽天チケット'"/>

    <div style="background-image:url(../static/bg_bar.gif);background-color:#bf0000" bgcolor="#bf0000"><font color="#ffffff" size="3"><font color="#ffc0cb">■</font>楽天チケット</font></div>

    <div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

    <%include file='../common/_search.mako' args="form=form, genre=form.genre.data, sub_genre=form.sub_genre.data"/>

        <div style="background-image:url(../static/bg_bar.gif);background-color:#bf0000" bgcolor="#bf0000"><font color="#ffffff" size="3"><font color="#ffbf00">■</font>ピックアップ</font></div>

        <div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

        % if form.promotions.data:
            % for promo in form.promotions.data:
                % if helper.get_event_from_promotion(request, promo):
                    <a href="/eventdetail?promotion_id=${promo.id}">${promo.text}</a>
                % else:
                    ${promo.text}
                % endif
            % endfor
        % endif

        <div style="background-image:url(../static/bg_bar.gif);background-color:#bf0000" bgcolor="#bf0000"><font color="#ffffff" size="3"><font color="#ffbf00">■</font>ジャンルから探す</font></div>

        <div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>
        % for genre in form.genretree.data:
            <a href="/genre?genre=${genre.id}">${genre.label}</a>｜
        % endfor

        <%include file="../common/_attention.mako" args="attentions=form.attentions.data
                                                        , genre=0, sub_genre=0, helper=helper"/>

        <%include file="../common/_area.mako" args="path=form.path.data, genre=form.genre.data
                            , sub_genre=form.sub_genre.data, num=form.num.data"/>

        <%include file="../common/_topics.mako" args="topics=form.topics.data
                                                         , genre=0, sub_genre=0, helper=helper"/>

        <%include file="../common/_hotward.mako" args="hotwords=form.hotwords.data, genre=0, sub_genre=0
                                                          , helper=helper" />

        <%include file="../common/_footer.mako"/>
    </body>
</html>
