<%inherit file="base.mako" />
<%
member_set = _context.member_sets[0]
guest_member_kinds = [member_kind for member_kind in member_set.member_kinds if member_kind.show_in_landing_page and member_kind.enable_guests]
%>

<p class="box bold tac fs18" style="color: red;">ファンクラブ連携が確認できません</p>

<p style="text-align:center">
<a href="/">トップへ戻る</a>
</p>

<!--SiteCatalyst-->
<%
    sc = {"pagename": "error-unknown"}
%>
<%include file="../common/sc_basic.html" args="sc=sc" />
<!--/SiteCatalyst-->
