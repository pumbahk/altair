<!DOCTYPE html>
<html>
    <%include file="../common/_header.mako" args="title=u'トップページ'"/>
    <body>
        トップ<p/>

        <%include file="../common/_search.mako" args="form=form" />
        <hr/>
        <h2>ピックアップ</h2>
            % if form.promotions.data:
                % for promo in form.promotions.data:
                    <a href="${promo.link}">${promo.text}</a>
                % endfor
            % endif
        <p/>
        <hr/>
            <h2>ジャンルから探す</h2>
                % for genre in form.genretree.data:
                    <a href="/genre?genre=${genre.id}">${genre.label}</a>｜
                % endfor
            <p/>
        <hr/>
        <%include file="../common/_attention.mako" args="attentions=form.attentions.data"/>
        <hr/>
        <%include file="../common/_area.mako" args="path=form.path.data, genre=form.genre.data
                            , sub_genre=form.sub_genre.data, num=form.num.data"/>
        <hr/>
        <%include file="../common/_topics.mako" args="topics=form.topics.data"/>
        <hr/>
        <%include file="../common/_hotward.mako" args="hotwords=form.hotwords.data" />

        <%include file="../common/_footer.mako"/>
    </body>
</html>