<%inherit file="base.mako" />
<% member_set = selected_member_set %>


<div class="box clearfix">


<!-- member LOGIN BOX -->
<div class="col2 login-box">
<dl>
<dt class="login-name"><span>各種会員IDをお持ちの方</span>はこちらから</dt>
<dd class="login-inbox">

<ul class="fcType clearfix">
<li class="fcType-L" style="background:#FFF1D7;"><img src="${view_context.static_url('images/status_soc.png')}" alt="SOC"></li>
<li class="fcType-L" style="background:#EEE6FF;"><img src="${view_context.static_url('images/status_stockholder.png')}" alt="株主優待"></li>
<li class="fcType-L" style="background:#CCD5DD;"><img src="${view_context.static_url('images/status_sponsor.png')}" alt="スポンサークラブ"></li>
<li class="fcType-L" style="background:#E1FFE1;"><img src="${view_context.static_url('images/status_school.png')}" alt="スクール"></li>
</ul>

<form action="${_context.route_path('extauth.login')}" method="POST">
<table class="loginTBL">
<tbody>
<tr>
<th>${h.auth_identifier_field_name(member_set)}</th>
<td>
  <input type="text" class="text" name="username" value="${username}" />
  % if message:
  <p>${message}</p>
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
</div>


<!-- stockholder LOGIN BOX -->
<div class="btn-stockholder">
<p class="clear tar pdt10 pdr20">&raquo; <a href="${_context.route_path('extauth.entry')}"><span>ファンクラブ会員の方、一般の方はコチラから</span></a></p>
</div>


</div>



<article class="box">
<h3 class="heading-bline">注意事項</h3>
<ul class="list-disc">
<li>会員の方も、受付番号（REから始まる12ケタ）から確認することができます。</li>
<li>会員ID・パスワードは半角でご入力ください。</li>
</ul>
</article>


<article class="box">
<h3 class="heading-bline">お問い合わせ</h3>
<ul class="list-disc">
<li>楽天野球団チケットセンター<br>
TEL: 050-5817-8192（平日10時～18時）※不定休</li>
</ul>
</article>

<!--SiteCatalyst-->
<%
    sc = {"pagename": "login"}
%>
<%include file="../common/sc_basic.html" args="sc=sc" />
<!--/SiteCatalyst-->
