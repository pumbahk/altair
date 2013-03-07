<!DOCTYPE html>
<html>
    <%include file="../common/_header.mako" args="title=u'トップページ'"/>
    <body>
        トップ<p/>

        <%include file="../common/_search.mako" args="form=form" />
        <hr/>
        <h2>ピックアップ</h2>
            % if promotions:
                % for promo in promotions:
                    <a href="${promo.link}">${promo.text}</a>
                % endfor
            % endif
        <p/>
        <hr/>
            <h2>ジャンルから探す</h2>
                % for genre in genres:
                    <a href="/genre?genre=${genre.id}">${genre.label}</a>｜
                % endfor
            <p/>
        <hr/>
        <%include file="../common/_attention.mako" args="attentions=attensions"/>
        <hr/>
        <%include file="../common/_area.mako" args="form=form"/>
        <hr/>
        <%include file="../common/_topics.mako" args="topics=topics"/>
        <hr/>
        <%include file="../common/_hotward.mako" args="hotwords=hotwords" />

        <%include file="../common/_footer.mako"/>
    </body>
</html>