<%inherit file="../common/_base.mako" />
<%namespace file="../common/tags_mobile.mako" name="m" />
<%block name="title">
% if form.dispsubgenre.data:
${form.dispsubgenre.data.label}
% else:
${form.dispgenre.data.label}
% endif
</%block>

<a href="http://ytj.tstar.jp/halloween/howto.html">購入方法</a><br><a href="http://ytj.tstar.jp/halloween/faq.html">よくある質問</a><br><a href="https://ytj.tstar.jp/orderreview">購入確認</a><br><a href="http://www.ytj.gr.jp/">公式サイトへ</a><br>

<%include file='../common/_attention.mako' args="attentions=form.attentions.data, genre=form.genre.data, sub_genre=form.sub_genre.data, helper=helper"/>
<%include file='../common/_hotward.mako' args="hotwords=form.hotwords.data, genre=form.genre.data, sub_genre=form.sub_genre.data, helper=helper"/>
