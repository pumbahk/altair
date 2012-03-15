<%inherit file="altaircms:templates/front/original5/base.mako"/>
<%namespace name="widget" file="altaircms:templates/front/original5/widgets.mako"/>

<%def name="widgets(name)">
  % for w in display_blocks[name]:
      ${w|n}
  % endfor
</%def>

<%block name="description">${widgets("description")}</%block>
<%block name="keywords">${widgets("keywords")}</%block>
<%block name="title">${widgets("title")}</%block>

<%block name="css_prerender">
  ${self.inherits.css_prerender()}
  <link rel="stylesheet" type="text/css" href="http://rakuten-ticket-static.s3.amazonaws.com/public/stylesheets/default.css" />
  <link rel="stylesheet" type="text/css" href="http://rakuten-ticket-static.s3.amazonaws.com/public/stylesheets/ui-lightness/jquery-ui-1.8.13.custom.css" />
  <link rel="stylesheet" type="text/css" href="http://rakuten-ticket-static.s3.amazonaws.com/public/stylesheets/order.css" />

  <style type="text/css">
   ${widgets("css_prerender")}

    table.ticketlist {
      margin-left: 50px;
      border-collapse: collapse;
      border: solid 1px #999;
      font-size: 100%;
    }
    table.ticketlist td.head {
      background: #BFBFBF;
      text-align: center;
      white-space: nowrap;
    }
    table.ticketlist th,
    table.ticketlist td {
      border: solid 1px;
      padding: 4px 6px;
    }
    /* menu */
    ul.menu {
        margin: 0;
        padding: 0;
        border-bottom: 2px #ddd solid;
    }
    ul.menu li {
        float: left;
        margin: 0 0 0 5px;
        position: relative;
        bottom: -2px;
        list-style-type: none;
        border: 1px #ddd solid;
        border-top: none;
        border-bottom: 2px #ddd solid;
    }
    ul.menu li.none {
        border-bottom: 2px #fff solid;
        font-weight: bold;
    }
    ul.menu li a {
        color: #000;
        display: block;
        padding: 3px 10px 5px;
        text-decoration: none;
        background: #fff;
    }
    ul.menu li a {
        border-bottom: 5px #dd1d25 solid;
    }
    ul.menu li a:hover {
        position: relative;
        bottom: 6px;
    }
    .clear {
        clear: both;
    }
  </style>
</%block>

<%block name="js_prerender">
  ${self.inherits.js_prerender()}
  <script type="text/javascript">
    var _tscn = 'ts93c91afd';
    (function(d,x,n,s){n=d.createElement('script'),n.type='text/javascript',n.src=x,n.async=true;s=d.getElementsByTagName("script")[0];s.parentNode.insertBefore(n,s);})(document,'https://secure.ticketstar.jp/-/b.js');
</script>
  <script type="text/javascript" src="http://rakuten-ticket-static.s3.amazonaws.com/public/javascripts/jquery-1.6.1.min.js"></script>
  <script type="text/javascript" src="http://rakuten-ticket-static.s3.amazonaws.com/public/javascripts/jquery-ui-1.8.13.custom.min.js"></script>
  <script src="http://cdn.jquerytools.org/1.2.6/full/jquery.tools.min.js"></script>
    ${widgets("js_prerender")}
</%block>

<%block name="js_postrender">
  ${self.inherits.js_postrender()}
  ${widgets("js_postrender")}
</%block>


<%block name="page_header_content">
## ここまだ対応していない。
    <div class="logo_and_globalnav">
      ${widget.logo()}
      ${widget.tagline()}
      ${widget.globalnav()}
    </div>
    ${widget.Rnavbar()}
    ${widget.navbar_and_search()}
    </div>
    ${widgets("page_header_content")}
</%block>

<%block name="notice">
    ${widgets("notice")}
</%block>

<%block name="page_main_header">
   <div class="page-main-header-content"></div>
    ${widgets("page_main_header")}
</%block>

<%block name="page_main_title">
   ${widgets("page_main_title")}
  ## ${ widget.social() }
</%block>

<%block name="page_main_image">
  ${widgets("page_main_image")}
  ## ${ widget.image() }
</%block>

<%block name="page_main_description">
  ${widgets("page_main_description")}
  ## ${ widget.description() }
</%block>

<%block name="page_main_performance_period">
  % if page.event:
    ${h.base.term(page.event.event_open,page.event.event_close)}
    (<a href="#performance-calendar">講演カレンダーを見る</a>)
  % endif
</%block>

<%block name="page_main_ticket_price">
  ${widgets("page_main_ticket_price")}
</%block>

<%block name="page_main_inquiry">
  % if page.event:
    ${h.base.nl_to_br(page.event.inquiry_for)|n}
  % endif
</%block>

<%block name="page_main_sales_period">
  % if page.event:
    ${h.base.term(page.event.deal_open,page.event.deal_close)}
  % endif
</%block>


<%block name="page_main_main">
  ${widgets("page_main_main")}
  ## ${ widget.summary()}
  ## ${ widget.performances()}
  ## ${ widget.calendar() }
</%block>

<%block name="page_main_footer">
  <div class="page-main-footer-content"></div>
</%block>

<%block name="page_footer">
  ${self.inherits.page_footer()}
</%block>

<%block name="js_footer">
  ${self.inherits.js_footer()}
  <script type="text/javascript">
    if("http:" == document.location.protocol) {
    document.write(unescape("%3Cimg src='http://grp02.trc.ashiato.rakuten.co.jp/svc-ashiato/trc?service_id=19'%3E"))
    }
    var _gaq = _gaq || [];_gaq.push(['_setAccount', 'UA-336834-1']);_gaq.push(['_trackPageview']);(function() { var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js'; var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);})();
  </script>
</%block>

### 
<%doc>
<%block name="@">
  ${self.inherits.@()}
</%block>
</%doc>
