<%inherit file="base.mako" />
<% member_set = selected_member_set %>
<section class="main idlogin">
<div class="wrap">
<div class="boxArea clearfix">
<div class="box">
<div class="login-box">
<dl>
<dt class="login-name"><span>各種会員IDをお持ちの方</span>はこちらから</dt>
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
<p><input type="submit" class="btnA btnA_l" value="ログイン"></p>
<input type="hidden" name="member_set" value="${selected_member_set.name}" />
<input type="hidden" name="_" value="${request.session.get_csrf_token()}" />
</form>
</dd>
</dl>
</div><!--/login-box -->
<p class="column">&raquo; <a href="${_context.route_path('extauth.entry')}"><span>一般の方はコチラから</span></a></p>
</div><!--/box -->

<article>
<h3 class="noteHead">注意事項</h3>
<ul class="noteList">
<li>会員の方も、受付番号（VEから始まる12ケタ）から確認することができます。</li>
<li>会員ID・パスワードは半角でご入力ください。</li>
</ul>
</article>
<article>
<h3 class="noteHead">お問い合わせ</h3>
<ul class="noteList">
<li>楽天ヴィッセルチケットセンター<br>TEL: 000-0000-0000（平日10時～18時）※不定休</li>
</ul>
</article>
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
