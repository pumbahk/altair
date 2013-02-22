<!DOCTYPE html>
<html>
    <%include file="../common/_header.mako" args="title=u'トップページ'"/>
    <body>
        <h2>
            <a href="/">トップ</a><p/>
        </h2>

        <%include file="../common/_search.mako" args="genre='', subgenre='', path='/search'" />
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
                <a href="/genre?genre=音楽">音楽</a>｜
                <a href="/genre?genre=スポーツ">スポーツ</a>｜
                <a href="/genre?genre=演劇・ステージ・舞台">演劇・ステージ・舞台</a>｜
                <a href="/genre?genre=その他イベント">その他イベント</a>
            <p/>
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