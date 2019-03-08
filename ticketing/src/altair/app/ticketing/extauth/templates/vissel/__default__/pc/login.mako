<%inherit file="base.mako" />
<% member_set = selected_member_set %>
<section class="main idlogin">
<div class="wrap">
<div class="boxArea clearfix">
<div class="box">
<div class="login-box">
<dl>
<dt class="login-name">${_(u'{}各種会員IDをお持ちの方{}はこちらから').format('<span>', '</span>')|n}</dt>
<dd class="login-inbox">
<!--<ul class="fcType clearfix">
<li class="fcType-L"><img src="" alt=""></li>
<li class="fcType-L"><img src="" alt=""></li>
<li class="fcType-L"><img src="" alt=""></li>
<li class="fcType-L"><img src="" alt=""></li>
</ul>//-->
<form action="${_context.route_path('extauth.login',_query=request.GET)}" method="POST">
<table class="loginTable">
<tbody>
<tr>
<th>${h.auth_identifier_field_name(member_set)}</th>
<td>
<input type="text" class="text" name="username" value="${username}" />
% if message:
<p class="red">${message}</p>
% endif
</td>
</tr>
<tr>
<th>${h.auth_secret_field_name(member_set)}</th>
<td><input type="password" name="password" value="${password}" /></td>
</tr>
</tbody>
</table>
<p><input type="submit" class="btnA btnA_l" value="${_(u'ログイン')}"></p>
<input type="hidden" name="member_set" value="${selected_member_set.name}" />
<input type="hidden" name="_" value="${request.session.get_csrf_token()}" />
</form>
</dd>
</dl>
</div><!--/login-box -->
<p class="column">&raquo; <a href="${_context.route_path('extauth.entry')}"><span>${_(u'一般の方はコチラから')}</span></a></p>
</div><!--/box -->

</div>
</div><!-- /wrap -->
<!-- back to top--><div id="topButton"><a>▲<br>上へ</a></div><!-- /back to top-->
</section><!-- /main -->

<!--SiteCatalyst-->
<%
    sc = {"pagename": "login"}
%>
<%include file="../common/sc_basic.html" args="sc=sc" />
<!--/SiteCatalyst-->
