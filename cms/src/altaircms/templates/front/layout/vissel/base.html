<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
## kadomaru
<%def name="widgets(name)">
  % for w in display_blocks[name]:
      ${w|n}
  % endfor
</%def>
<html lang="jp">
<head>
    <meta http-equiv="Content-Type" content="text/html;charset=UTF-8">
    <link rel="stylesheet" type="text/css" href="/static/vissel/css/style.css" media="all" />
    <title>${page.title}</title>
  <meta name="description" content="${page.description}">
  <meta name="keywords" content="${page.keywords}">
    <!--[if lte IE 6]>  
    <script type="text/javascript" src="/static/vissel/js/DD_belatedPNG.js">  
    </script>  
    <script type="text/javascript"> DD_belatedPNG.fix( '.header,.sparkle');</script>  
    <![endif]-->
    <script type="text/javascript">
var _gaq = _gaq || [];
_gaq.push(['_setAccount', 'UA-38527066-1']);
_gaq.push(['_trackPageview']);
</script>
</head>
<body>
    <div class="header">
        <div class="header-inner">
            <img src="/static/vissel/images/logo.gif" alt="VISSEL TICKET" />
            <div class="gnavi">
%for c in myhelper._get_categories(request, "header_large_button"):
    ${h.link.get_link_tag_from_category(request,c)}
     <br />
%endfor

                <ul>
##todo: helper
<% cs = list(myhelper._get_categories(request, "header_menu")) %>
%if len(cs) >= 2:
    <li class="first">${h.link.get_link_tag_from_category(request,cs[0])}</li>
    %for c in cs[1:-1]:
        <li>${h.link.get_link_tag_from_category(request,c)}</li>
    %endfor
    <li class="last">${h.link.get_link_tag_from_category(request,cs[-1])}</li>
%else:
    %for c in cs:
        <li class="first last">${h.link.get_link_tag_from_category(request,c)}</li>
    %endfor
%endif
                </ul>　　
            </div>
            <img src="/static/vissel/images/partnerlogo.gif" alt="OFFICIAL TICKET SITE PARTNER TICKETSTAR" class="partnerlogo" />
        </div>
    </div>

    <!-- wrapper -->    
    <div class="wrapper">
      <%block name="above_kadomaru">
        ${widgets("above_kadomaru")}
      </%block>

      <div class="kadomaru">
        <div class="maincol">
        <%block name="kadomaru">
          ${widgets("kadomaru")}
        </%block>
        </div>
      <!-- サイドバー -->
        <div class="sidebar">
          %for c in  myhelper._get_categories(request, "side_menu"):
            ${h.link.get_link_tag_from_category(request,c)}
          %endfor 

          %for c in  myhelper._get_categories(request, "side_banner"):
            ${h.link.get_link_tag_from_category(request,c)}
          %endfor 
        </div>  
      <!-- サイドバーおわり -->
      <br class="clear" />
    </div>
    <%block name="bellow_kadomaru">
      ${widgets("bellow_kadomaru")}
    </%block>
  </div>
    <!-- wrapperおわり -->


<div class="footer">
    <div class="footer-inner">
        <img src="/static/vissel/images/tomoni.gif" alt="" />
            <div class="footernav">
              <ul>
                 <% xs = myhelper._get_categories(request, "footer_menu").all()%>
                  %if len(xs) >= 2:
                    <li><a class="first" href="${h.link.get_link_from_category(request,xs[0])}">${xs[0].label}</a></li>
                    %for c in xs[1:-1]:
                            <li><a href="${h.link.get_link_from_category(request,c)}">${c.label}</a></li>
                    %endfor
                    <li><a class="last" href="${h.link.get_link_from_category(request,xs[-1])}">${xs[-1].label}</a></li>
                  %else:
                    %for c in xs:
                      <li><a class="first last" href="${h.link.get_link_from_category(request,c)}">${c.label}</a></li>
                    %endfor
                  %endif
              </ul>
            </div>
        <div class="copyright">
            Copyright &copy; 2010-2013 TicketStar Inc. All Rights Reserved. 
        </div>
    </div>
</div>
<script type="text/javascript">
(function() { var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true; ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js'; var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s); })();</script>
</body>
</html>
