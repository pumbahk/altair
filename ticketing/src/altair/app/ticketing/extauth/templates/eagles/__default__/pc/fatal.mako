<%inherit file="base.mako" />
<div class="errorBox">
<p class="errorText">致命的なエラーが発生しました</p>
</div>

<!--SiteCatalyst-->
<%
    sc = {"pagename": "error-fatal"}
%>
<%include file="../common/sc_basic.html" args="sc=sc" />
<!--/SiteCatalyst-->
