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
	<div id="grpheader">
  	  ${co.master_header()}
    </div>
    ${co.global_navigation(top_inner_categories, categories)}
    ${co.header_search()}
	<!-- ========== /header ========== -->

	<hr />

	<!-- ========== main ========== --> 
	<div id="main" style="margin-top: 20px;">

<%block name="topicPath">
  ${widgets("topicPath")}
</%block>

<%block name="main">
   ${widgets("main")}
</%block>
	</div>
	<!-- ========== /main ========== -->

	<hr />

	<!-- ========== side ========== -->
	<div id="side" style="margin-top: 20px;">
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
