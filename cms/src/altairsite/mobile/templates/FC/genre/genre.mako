<%inherit file="../common/_base.mako" />
<%namespace file="../common/tags_mobile.mako" name="m" />
<%block name="title">
% if form.dispsubgenre.data:
${form.dispsubgenre.data.label}
% else:
${form.dispgenre.data.label}
% endif
</%block>
<%block name="fnavi">
% if form.dispsubgenre.data:
[0]<a href="/genre?genre=${form.dispgenre.data.id}" accesskey="0">${form.dispgenre.data.label}</a></a><br />
% endif
[9]<a href="/" accesskey="9">トップへ</a><br />
</%block>

<%include file='../common/_attention.mako' args="attentions=form.attentions.data, genre=form.genre.data, sub_genre=form.sub_genre.data, helper=helper"/> 
<%m:header>サブジャンルで絞り込む</%m:header>

% for subgenre in form.genretree.data:
    <a href="/genre?genre=${form.dispgenre.data.id}&sub_genre=${subgenre.id}">${subgenre.label}</a>｜
% endfor

<%include file='../common/_topics.mako' args="topics=form.topics.data, genre=form.genre.data, sub_genre=form.sub_genre.data, helper=helper"/> 
<%include file="../common/_area.mako" args="path=form.path.data, genre=form.genre.data, sub_genre=form.sub_genre.data, num=form.num.data"/> 
<%include file='../common/_search.mako' args="form=form, genre=form.genre.data, sub_genre=form.sub_genre.data"/>
<%include file='../common/_hotward.mako' args="hotwords=form.hotwords.data, genre=form.genre.data, sub_genre=form.sub_genre.data, helper=helper"/>
