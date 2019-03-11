<%inherit file="base.mako" />
<%
member_set = _context.member_sets[0]
guest_member_kinds = [member_kind for member_kind in member_set.member_kinds if member_kind.show_in_landing_page and member_kind.enable_guests]
%>

<section class="main error">
<div class="wrap">
<p class="errorText">${_(u'ファンクラブ連携が確認できません')}（V011）</p>

<p style="text-align:center">
<a href="/">${_(u'トップへ戻る')}</a>
</p>
</div><!-- /wrap -->
</section><!-- /main -->

<!--SiteCatalyst-->
<%
    sc = {"pagename": "error-unknown"}
%>
<%include file="../common/sc_basic.html" args="sc=sc" />
<!--/SiteCatalyst-->
