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
</%block>

<%block name="js_prerender">
  ${self.inherits.js_prerender()}
  <script type="text/javascript">
    var _tscn = 'ts93c91afd';
    (function(d,x,n,s){n=d.createElement('script'),n.type='text/javascript',n.src=x,n.async=true;s=d.getElementsByTagName("script")[0];s.parentNode.insertBefore(n,s);})(document,'https://secure.ticketstar.jp/-/b.js');
</script>
  <script type="text/javascript" src="http://rakuten-ticket-static.s3.amazonaws.com/public/javascripts/jquery-1.6.1.min.js"></script>
  <script type="text/javascript" src="http://rakuten-ticket-static.s3.amazonaws.com/public/javascripts/jquery-ui-1.8.13.custom.min.js"></script>
</%block>


<%block name="page_header_content">
    <div class="logo_and_globalnav">
      ${widget.logo()}
      ${widget.tagline()}
      ${widget.globalnav()}
    </div>
    ${widget.Rnavbar()}
    ${widget.navbar_and_search()}
    </div>
</%block>

<%block name="notice">
</%block>

<%block name="page_main_header">
        <div class="page-main-header-content"></div>
</%block>
<%block name="page_main_main">
          ${display_blocks["page_main_main"][0]|n}
          ${ widget.social() }
          ${ widget.description_and_image() }
          ${ widget.summary()}
          ${display_blocks["page_main_main"][2]|n}
          ${ widget.performances()}
          ${display_blocks["page_main_main"][1]|n}
          ${ widget.calendar() }
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
