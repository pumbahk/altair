<%inherit file="base.mako" />

<section class="main fclogin">
<div class="wrap">
<div class="box">
<p class="lead">ファンクラブ会員を選択してください</p>
<ul class="statusList">
%for membership in memberships:
<li class="${membership['kind']['aux']['style_class_name']}">
<a href="${_context.route_path('extauth.authorize', _query=dict(_=request.session.get_csrf_token(), member_kind_id=membership['kind']['id'], membership_id=membership['membership_id']))}">
  <span class="member_kind">${membership['kind']['name']}</span>
  <span class="member_id tac">会員ID：${membership['displayed_membership_id']}</span>
</a>
</li>
%endfor
</ul>
</div><!-- /box -->
</div><!-- /wrap -->
<!-- back to top--><div id="topButton"><a>▲<br>上へ</a></div><!-- /back to top-->
</section><!-- /main -->

<!--SiteCatalyst-->
<%
    sc = {"pagename": "select_accoun"}
%>
<%include file="../common/sc_basic.html" args="sc=sc" />
<!--/SiteCatalyst-->
