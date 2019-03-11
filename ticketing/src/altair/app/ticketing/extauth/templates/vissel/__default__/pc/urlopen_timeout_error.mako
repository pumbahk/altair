<%inherit file="base.mako" />
<section class="main error">
<div class="wrap">
<p class="errorText">${_(u'ただいま大変込み合っております。')}（V006）</p>
${_(u'アクセス混雑などのため、現在ページが表示しにくい状態となっております。')}<br/>
${_(u'お客様にはご迷惑をおかけしますが、今しばらくお待ち頂き、再度アクセスをお願いいたします。')}<br/>
</div><!-- /wrap -->
</section><!-- /main -->

<!--SiteCatalyst-->
<%
    sc = {"pagename": "urlopen_timeout_error"}
%>
<%include file="../common/sc_basic.html" args="sc=sc" />
<!--/SiteCatalyst-->
