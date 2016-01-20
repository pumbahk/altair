<%inherit file="base.mako" />
<%
member_set = _context.member_sets[0]
guest_member_kinds = [member_kind for member_kind in member_set.member_kinds if member_kind.show_in_landing_page and member_kind.enable_guests]
%>

<p class="box bold tac fs18" style="color: red;">有効なファンクラブが確認できません</p>


<div class="box clearfix">
<p style="text-align:center">
※ファンクラブに入会をご希望の方は<a href="http://www.rakuteneagles.jp/fanclub/">こちら</a>から
</p>
</div>
