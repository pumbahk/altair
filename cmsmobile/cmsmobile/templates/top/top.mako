<!DOCTYPE html>
<html>
    <%include file="../common/_header.mako" args="title=u'楽天チケット'"/>

        <%include file="../common/_search.mako" args="form=form" />

        <div style="background-image:url(../static/bg_bar.gif);background-color:#bf0000;font-size: medium;
            color: #ffffff" bgcolor="#bf0000" background="../static/bg_bar.gif">ピックアップ</div>

            <span style="font-size: x-small">
                % if form.promotions.data:
                    % for promo in form.promotions.data:
                        % if promo.link:
                            <a href="${promo.link}">${promo.text}</a>
                        % else:
                            ${promo.text}
                        % endif
                    % endfor
                % endif
            </span>

            <div style="background-image:url(../static/bg_bar.gif);background-color:#bf0000;font-size: medium;
                        color: #ffffff" bgcolor="#bf0000" background="../static/bg_bar.gif">ジャンルから探す</div>
                <span style="font-size: x-small">
                    % for genre in form.genretree.data:
                        <a href="/genre?genre=${genre.id}">${genre.label}</a>｜
                    % endfor
                </span>

        <%include file="../common/_attention.mako" args="attentions=form.attentions.data"/>

        <%include file="../common/_area.mako" args="path=form.path.data, genre=form.genre.data
                            , sub_genre=form.sub_genre.data, num=form.num.data"/>

        <%include file="../common/_topics.mako" args="topics=form.topics.data"/>

        <%include file="../common/_hotward.mako" args="hotwords=form.hotwords.data" />

        <%include file="../common/_footer.mako"/>
    </body>
</html>