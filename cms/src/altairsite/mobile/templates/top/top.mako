<%inherit file="../common/_base.mako" />
<%namespace file="../common/tags_mobile.mako" name="m" />
<%block name="title">楽天チケットトップ</%block>
<div style="background-image:url(/static/mobile/bg_bar.gif);background-color:#bf0000;
            color: #ffffff" bgcolor="#bf0000" background="/static/mobile/bg_bar.gif"></div>
<div align="center">楽天チケットへようこそ</div>
<div>
├<a href="https://member.id.rakuten.co.jp/rms/mid/vc?__event=regist&c2=313131784">楽天会員登録 (無料)</a><br />
├<a href="/order">購入履歴確認</a><br />
└<a href="/information">中止・変更情報</a><br />
</div>
<br />
<%include file='../common/_search.mako' args="form=form, genre=form.genre.data, sub_genre=form.sub_genre.data"/>

<%m:header>ピックアップ</%m:header>
% if form.promotions.data:
    % for count, promo in enumerate(form.promotions.data):
        % if helper.get_event_from_promotion(request, promo):
            <a href="/eventdetail?event_id=${helper.get_event_from_promotion(request, promo).id}">${promo.text}</a><br />
        % endif
    % endfor
% endif

<%m:header>ジャンルから探す</%m:header>
% for i in range(0, len(form.genretree.data)):
<% genre = form.genretree.data[i] %>
${u'├' if i != len(form.genretree.data) - 1 else u'└'}<a href="/genre?genre=${genre.id}">${genre.label}</a><br />
% endfor
<%include file="../common/_attention.mako" args="attentions=form.attentions.data, genre=0, sub_genre=0, helper=helper"/>
<%include file="../common/_area.mako" args="path=form.path.data, genre=form.genre.data, sub_genre=form.sub_genre.data, num=form.num.data"/>
<%include file="../common/_topics.mako" args="topics=form.topics.data, genre=0, sub_genre=0, helper=helper"/>
<%include file="../common/_hotward.mako" args="hotwords=form.hotwords.data, genre=0, sub_genre=0, helper=helper" />
