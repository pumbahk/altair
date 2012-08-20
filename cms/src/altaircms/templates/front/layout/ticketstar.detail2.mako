<%def name="widgets(name)">
  % for w in display_blocks[name]:
      ${w|n}
  % endfor
</%def>

#### blocks
## info {description,keywords,title  }
## custom {css_prerender,js_prerender}
## header{subCategoryMenulist, topicPath}
## + main_top,main_bottom,main_left,main_right,footer


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

	<%block name="js_prerender"/>
	<%block name="css_prerender"/>

	<style type="text/css">
	  h1 {font-size:200%; }
	  h2 {font-size:170%; }

      #main_left img{max-width:380px; max-height:285px;}
      #main_right img{max-width:250px; max-height:187px;}

      #main_left p {width:380px;}
      #main_right p {width:250px;}

	  #main_left{width:58%; float: left;}
	  #main_right{width:38%; float: left;}
      .clear{clear:both;  }
    </style>
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
<div id="main_top">
  <%block name="main_top">
  ${widgets("main_top")}
  </%block>
</div>
<div id="main_left">
  <%block name="main_left">
  ${widgets("main_left")}
  </%block>
</div>
<div id="main_right">
  <%block name="main_right">
  ${widgets("main_right")}
  </%block>
</div>
<div class="clear"></div>
<div id="main_bottom">
  <%block name="main_bottom">
  ${widgets("main_bottom")}
  </%block>
</div>

	</div>
	<!-- ========== /main ========== -->

	<hr />

	<!-- ========== side ========== -->
	<div id="side"  style="margin-top: 20px;">
<%block name="side">
    ${widgets("side")}
</%block>
	</div>
	<!-- ========== /side ========== -->

	<hr />

	<!-- ========== footer ========== -->
	${co.master_footer()}
	<!-- ========== /footer ========== -->
<%block name="footer">
    ${widgets("footer")}
</%block>
	<!-- /container --></div>
  </body>
</html>
