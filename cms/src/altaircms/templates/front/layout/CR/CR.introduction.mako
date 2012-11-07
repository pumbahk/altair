<%def name="widgets(name)">
  % for w in display_blocks[name]:
      ${w|n}
  % endfor
</%def>

## above_kadomaru, card_and_QR,card_and_seven,card_and_home,anshin_and_QR,anshin_and_seven,anshin_and_home,seven_and_seven

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html lang="jp">
<head>
	<meta http-equiv="Content-Type" content="text/html;charset=UTF-8">
	<link rel="stylesheet" type="text/css" href="/static/CR/css/style.css" media="all" />
	    <title>${page.title}</title>    <meta name="description" content="${page.description}">    <meta name="keywords" content="${page.keywords}">

<script type="text/javascript">
  $(function(){
    var e = $("<a>");
    e.attr("href","http://tokyo-cinqreves.jp/")
    e.css({"position": "relative",
	  "top": "10px",
	  "left": "50px",
    "display": "block",
    "width": "140px",
    "height": "100px",
     });
    $(".header").append(e);
   });
</script>

</head>
<body>
	<!-- wrapper -->	
	<div class="wrapper">
		<!-- メインカラム -->
		<div class="maincol">
			<div class="header">
				<div class="gnavi">
					<ul>
%for c in myhelper._get_categories(request, "header_menu"):
	<li><a href="${h.link.get_link_from_category(request,c)}">${c.label}</a></li>
%endfor
					</ul>　　
				</div>
			</div>

<%block name="above_kadomaru">
  ${widgets("above_kadomaru")}
</%block>

			<div class="kadomaru">

<%block name="card_and_QR">
  ${widgets("card_and_QR")}
</%block>

<%block name="card_and_seven">
  ${widgets("card_and_seven")}
</%block>

<%block name="card_and_home">
  ${widgets("card_and_home")}
</%block>

<%block name="anshin_and_QR">
  ${widgets("anshin_and_QR")}
</%block>

<%block name="anshin_and_seven">
  ${widgets("anshin_and_seven")}
</%block>

<%block name="anshin_and_home">
  ${widgets("anshin_and_home")}
</%block>

<%block name="seven_and_seven">
  ${widgets("seven_and_seven")}
</%block>

</div>
<!-- kadomaruおわり -->

			<div class="footer">
				<div class="footernav">
		          <ul>
		            <li class="first"><a href="/static/faq/faq.html">ヘルプ</a></li>
		            <li><a href="http://www.ticketstar.jp/corporate">運営会社</a></li>
		            <li><a href="https://ticket.rakuten.co.jp/contact/form">お問い合わせ</a></li>
		            <li><a href="http://www.ticketstar.jp/privacy">個人情報保護方針</a></li>
		            <li class="last"><a href="http://www.ticketstar.jp/legal">特定商取引法に基づく表示</a></li>
		          </ul>
		        </div>
				<div class="copyright">
					Copyright &copy; 2010-2011 TicketStar Inc. All Rights Reserved. 
				</div>
			</div>

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
