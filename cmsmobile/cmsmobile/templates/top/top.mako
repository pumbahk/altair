<!DOCTYPE html>
<html>
    <%include file="../common/_header.mako" args="title=u'楽天チケット'"/>

        <%include file="../common/_search.mako" args="form=form" />

        <div style="background-image:url(../static/bg_bar.gif);background-color:#bf0000;
            color: #ffffff" bgcolor="#bf0000" background="../static/bg_bar.gif">ピックアップ</div>

        <div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

        % if form.promotions.data:
            % for promo in form.promotions.data:
                <a href="/eventdetail?promotion_id=${promo.id}">${promo.text}</a>
            % endfor
        % endif

        <div style="background-image:url(../static/bg_bar.gif);background-color:#bf0000;
                    color: #ffffff" bgcolor="#bf0000" background="../static/bg_bar.gif">ジャンルから探す</div>

        <div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>
        % for genre in form.genretree.data:
            <a href="/genre?genre=${genre.id}">${genre.label}</a>｜
        % endfor

        <%include file="../common/_attention.mako" args="attentions=form.attentions.data"/>

        <%include file="../common/_area.mako" args="path=form.path.data, genre=form.genre.data
                            , sub_genre=form.sub_genre.data, num=form.num.data"/>

        <%include file="../common/_topics.mako" args="topics=form.topics.data"/>

        <%include file="../common/_hotward.mako" args="hotwords=form.hotwords.data" />

        <%include file="../common/_footer.mako"/>
    </body>
</html>