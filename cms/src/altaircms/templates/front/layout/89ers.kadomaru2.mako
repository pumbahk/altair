## above_kadomaru,kadomaru,below_kadomaru
<%def name="widgets(name)">
  % for w in display_blocks[name]:
      ${w|n}
  % endfor
</%def>

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html lang="jp">
<head>
	<meta http-equiv="Content-Type" content="text/html;charset=UTF-8">
	<link rel="stylesheet" type="text/css" href="/static/89ers/css/style.css" media="all" />
	<title>${page.title}</title>     <meta name="description" content="${page.description}">     <meta name="keywords" content="${page.keywords}">
<script type="text/javascript">
     $(function(){
var e = $("<a>");
e.attr("href","http://www.89ers.jp/")
e.css({"position": "relative",
       "display": "block",
       "width": "165px",
       "height": "100px",
       "margin-left": "50px"
       });
$("header").append(e);
     });
   </script>
</head>

<body>
	<!-- wrapper -->	
	<div class="wrapper">
		<!-- メインカラム -->
		<div class="maincol">
			<header>
				<div class="gnavi">
					<ul>
%for c in myhelper._get_categories(request, "header_menu"):
	<li><a href="${h.link.get_link_from_category(request,c)}">${c.label}</a></li>
%endfor
					</ul>　　
				</div>
			</header>

			  <%block name="above_kadomaru">
                ${widgets("above_kadomaru")}
			  </%block>

			<div class="kadomaru">
			  <%block name="kadomaru">
                ${widgets("kadomaru")}
			  </%block>
			</div>
			<div class="kadomaru">
			  <%block name="kadomaru2">
                ${widgets("kadomaru2")}
			  </%block>
			</div>
			<!-- kadomaru終わり -->

			  <%block name="below_kadomaru">
                ${widgets("below_kadomaru")}
			  </%block>


			<footer>
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
					Copyright &copy; 2010-2011 TicketStar Inc. All Rights Reserved. 
				</div>
			</footer>

		</div>
		<!-- メインカラムおわり -->
		<!-- サイドバー -->
		<div class="sidebar">
			
			
			
		</div>	
		<!-- サイドバーおわり -->
		
	</div>
	<!-- wrapperおわり -->
</body>
</html>
