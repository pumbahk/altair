<%def name="widgets(name)">
  % for w in display_blocks[name]:
      ${w|n}
  % endfor
</%def>

#### blocks
## info {description,keywords,title  }
## custom {css_prerender,js_prerender}
## header{subCategoryMenulist, topicPath}
## + main
## + side
## + userBox
## + footer

<%namespace file="../ticketstar/components.mako" name="co"/>

<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="ja" lang="ja">
  <head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8" />
    
    <title>${page.title}</title>
    <meta name="description" content="${page.description}">
    <meta name="keywords" content="${page.keywords}">
        
    <meta http-equiv="content-style-type" content="text/css" />
    <meta http-equiv="content-script-type" content="text/javascript" />
    <link rel="shortcut icon" href="/static/ticketstar/img/common/favicon.ico" />
    <link rel="stylesheet" href="/static/ticketstar/css/import.css" type="text/css" media="all" />

    <style type="text/css">
	  h1 {font-size:200%; }
	  h2 {font-size:170%; }
    </style>

	<%block name="js_prerender"/>
	<%block name="css_prerender"/>
  </head>

  <body id="detail">
	<p id="naviSkip"><a href="#main" tabindex="1" title="本文へジャンプ"><img src="/static/ticketstar/img/common/skip.gif" alt="本文へジャンプ" width="1" height="1" /></a></p>

	<div id="container">

	  <!-- ========== header ========== -->
	  <%block name="header">
	  <div id="grpheader">
		${co.master_header(top_outer_categories)}
        ${co.section_navigation()}
		<dl id="subSectionNav">
		  <dt>サブカテゴリー</dt>
		  <dd class="menuList">
			<ul>
			  <% nav_categories = list(categories)%>
				% for category in nav_categories[:-1]:
				  <li><a href="${h.link.get_link_from_category(request, category)}" alt="${category.label}">${category.label}</a></li>
				% endfor
				% if categories:
				  <li><a href="${h.link.get_link_from_category(request, nav_categories[-1])}" alt="${nav_categories[-1].label}">${nav_categories[-1].label}</a></li>
				% endif
			</ul>
		  </dd>
		</dl>
		<dl id="topicPath">
		  <dt>現在地</dt>
		  <dd>
<%block name="topicPath">
  ${widgets("topicPath")}
</%block>
		  </dd>
		</dl>
	  </div>
	</%block>
	<!-- ========== /header ========== -->

	<hr />

	<!-- ========== main ========== --> 
	<div id="main">
<%block name="main">
   ${widgets("main")}
</%block>
	</div>
	<!-- ========== /main ========== -->

	<hr />

	<!-- ========== side ========== -->
	<div id="side">
<%block name="side">
    ${widgets("side")}
</%block>
	</div>
	<!-- ========== /side ========== -->

	<div id="userBox">
<%block name="userBox">
    ${widgets("userBox")}
</%block>
	</div>  
	<hr />

	<!-- ========== footer ========== -->
	${co.master_footer()}
	<!-- ========== /footer ========== -->

	<!-- /container --></div>
  </body>
</html>
