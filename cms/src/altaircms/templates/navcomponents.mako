## breadcrumbs
<%def name="breadcrumbs(names=[], urls=[])">
  <ul class="breadcrumb">
    % for i in xrange(len(urls)):
      <li><a href="${urls[i]}">${names[i]}</a><span class="divider">/</span></li>
    % endfor

    <li>${names[-1]}</li>
 </ul>
</%def>

## sidebar
<%def name="sidebar(request)">
  <ul class="nav nav-list">
    <li class="nav-header">イベント管理</li>
    <!-- <li><a href="/client">edit client</a></li> -->
    <li><a href="${request.route_path("event_list")}">イベント</a></li>
    <li><a href="${request.route_path("performance_list")}">パフォーマンス</a></li>
    <li><a href="${request.route_path("ticket_list")}">チケット</a></li>
    <li class="nav-header">ページ管理</li>
    <li><a href="${request.route_path("page")}">ページ</a></li>
    <li><a href="${request.route_path("pagesets")}">ページセット</a></li>
	<li class="nav-header">トピック管理</li>
    <li><a href="${request.route_path("promotion_list")}">プロモーション枠</a></li>
    <li><a href="${request.route_path("promotion_unit_list")}">プロモーション</a></li>
    <li><a href="${request.route_path("topic_list")}">トピック</a></li>
    <li><a href="${request.route_path("topcontent_list")}">トップコンテンツ</a></li>
    <li><a href="${request.route_path("hotword_list")}">ホットワード</a></li>

    <li class="nav-header">アセット管理</li>
    <li><a href="${request.route_path("asset_list")}">アセット</a></li>
    <li><a href="${request.route_path("tag", classifier="top")}">タグ</a></li>
	<li class="nav-header">マスター</li>
    <li><a href="${request.route_path("layout_list")}">レイアウト</a></li>
    <li><a href="${request.route_path("pagedefaultinfo_list")}">ページのurlmapping</a></li>
	
    <li><a href="${request.route_path("category_list")}">カテゴリー</a></li>
    <!-- <li><a href="#">メールマガジン</a></li> -->
    <li><a href="${request.route_path("operator_list")}">オペレータ</a></li>
    <li><a href="${request.route_path("apikey_list")}">APIKEY</a></li>
    <li><a href="${request.route_path("role_list")}">ロール</a></li>
  </ul>
</%def>


## flash message
##
<%def name="alert(css_kls, messages)">
  %if messages:
	<div class="${css_kls}">
	  <a class="close" data-dismiss="alert">×</a>
	  %for mes in messages:
		<p>${mes}</p>
	  %endfor
   </div>
 %endif
</%def>

<%def name="flashmessage(classname='flashmessage')">
  <div class="${classname}">
	${alert("alert alert-block alert-success",   request.session.pop_flash("successmessage"))}
	${alert("alert alert-block alert-info",   request.session.pop_flash("infomessage"))}
	${alert("alert alert-block alert-error", request.session.pop_flash("errormessage"))}
  </div>
</%def>

## footer
<%def name="footer()">
  <hr>
  <footer>
  &copy; 2012 TicketStar Inc.
  </footer>
</%def>

## header
<%def name="header()">
  <div class="navbar navbar-fixed-top">
	<div class="navbar-inner">
	  <div class="container">
		<a class="brand" href="/cms"><img src="/static/img/altair_logo.png"></a>
		<div class="nav-collapse">
		  <ul class="nav pull-right">
			  % if user:
				<li class="dropdown">
				  <a href="#" class="dropdown-toggle" data-toggle="dropdown">${user.screen_name}<b class="caret"></b></a>
				  <ul class="dropdown-menu">
					<li><a href="#">
					  <i class="icon-cog"> </i>
					  Settings</a>
					</li>
					<li><a href="${request.route_path("logout")}">
					  <i class="icon-off"> </i>
					  Logout</a>
					</li>
				  </ul>
				</li>
			  % else:
				<li><a href="${request.route_path("oauth_entry")}">Login with OAuth</a></li>
			  % endif
		  </ul>
		</div><!--/.nav-collapse -->
		  <!-- Navigation -->
		  <div id="navigation">
			<ul>
			  <li><a href=""><span>ダッシュボード</span></a></li>
			  <li><a href="/"><span>票券管理</span></a></li>
			  <li><a href="/cms" class="active"><span>CMS</span></a></li>
			</ul>
		  </div>
		  <!-- End Navigation -->
	  </div>
	</div>
  </div>
</%def>
