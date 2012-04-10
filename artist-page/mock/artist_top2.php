<?php
$dbh = mysql_connect("127.0.0.1:3306", "root", 'root');
mysql_selectdb("artistpage");
mysql_set_charset( "UTF8", $dbh );

$l = "select * from g where parent_id = 0";
$d = mysql_query($l,$dbh);
$r=0;
$t = array();
  while($row=mysql_fetch_assoc($d)){
	echo($row['genre']);
	$t[$r] = $row['genre'];
	echo "<br>";
	$r++;
	}

?>
<html>
<head>
<link rel="stylesheet" href="artist_top.css" type="text/css" />
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<script type="text/javascript" src="http://www.google.com/jsapi"></script>  
<script type="text/javascript">google.load("jquery", "1.2");</script>
<script type="text/javascript" src="artist_top.js"></script>
<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.5.0/jquery.min.js"></script>
</head>
<body>
<div id = "container">
	<div id ="mainbox">
		<div id="page_hanbetu">トップページ</div>
		<div id ="header">
			<ul>
					<a href="#.html"><li>＊＊＊  </li></a>	<a href="#.html"><li>＊＊＊</li></a>	<a href="#.html"><li>＊＊＊</li></a>	
			</ul>
		</div>
		<div id ="kensaku" >
			<form action="http://www.goo.ne.jp/default.asp">
			
			<input type=text name="MT" size=20>
			<input type=submit value="検索" name="act.search">
			<input type="hidden" name="SM" value="MC">
			<input type="hidden" name="RD" value="DM">
			<input type="hidden" name="Domain" value="www.tohoho-web.com">
			<input type="hidden" name="Path" value="">
			<input type="hidden" name="from" value="USR">
			<input type="hidden" name="DC" value="50">
		</form>
	</div>
	<div id = "tx_left">
		<ul>
		<? for($q=0;$q<=11;$q++): ?>
			 
			<li id ='#'><a href ='./genre.php?genre=<?=urlencode($t[$q])?>'><?= htmlspecialchars($t[$q]); ?></a></li>
			
		<? endfor ?>
	
		</ul>
		
					
	
	</div>

	<div id = "tx_center">
		<div id =" top_news" >
		
			<table>
				<tr>
					<td>
					<img src ="./img/4.png" width = 25 height = 25>
					<a href ="news.html">加藤ミリヤがチャリティコンサート</a>
					</td>
					<td>
					<img src ="./img/4.png" width = 25 height = 25>
					<a href ="news.html">AKBチャート二曲入り</a>
					</td>
					<td>
					<img src ="./img/4.png" width = 25 height = 25>
					<a href ="news.html">AKBチャート二曲入り</a>
					</td>
					<td>
					<img src ="./img/2.png" width = 25 height = 25>
					<a href ="news.html">安室奈美恵が結婚</a>
					</td>
					</tr>
					<tr>
					<td>
					<img src ="./img/4.png" width = 25 height = 25>
					<a href ="news.html">AKBチャート二曲入り</a>
					</td>
					<td>
					<img src ="./img/2.png" width = 25 height = 25>
					<a href ="news.html">BUMPCD選考予約</a>
					</td>
					<td>
					<img src ="./img/6.png" width = 25 height = 25>
					<a href ="news.html">YUKI 10周年記念</a>
					</td>
					<td>
					<img src ="./img/5.png" width = 25 height = 25>
					<a href ="news.html">夜明けのスキャット　チャート1位</a>
					</td>
				</tr>
			</table>
			<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.5.0/jquery.min.js"></script>
			<script type="text/javascript">
			$(function(){
			$('#carousel').each(function(){
				var slideTime = 200;
				var delayTime = 2000;
				var carouselWidth = $(this).width();
				var carouselHeight = $(this).height();
				$(this).append('<div id="carousel_prev"></div><div id="carousel_next"></div>');
				$(this).children('ul').wrapAll('<div id="carousel_wrap"><div id="carousel_move"></div></div>');

				$('#carousel_wrap').css({
				width: (carouselWidth),
				height: (carouselHeight),
				position: 'relative',
				overflow: 'hidden'
				});

				var listWidth = parseInt($('#carousel_move').children('ul').children('li').css('width'));
				var listCount = $('#carousel_move').children('ul').children('li').length;

				var ulWidth = (listWidth)*(listCount);

				$('#carousel_move').css({
				top: '0',
				left: '-38',
				width: ((ulWidth)*3),
				height: (carouselHeight),
				position: 'absolute'
				});

				$('#carousel_wrap ul').css({
				width: (ulWidth),
				float: 'left'
				});
				$('#carousel_wrap ul').each(function(){
				$(this).clone().prependTo('#carousel_move');
				$(this).clone().appendTo('#carousel_move');
				});

				carouselPosition();

				$('#carousel_prev').click(function(){
				clearInterval(setTimer);
				$('#carousel_move:not(:animated)').animate({left: '+=' + (listWidth)},slideTime,function(){
				carouselPosition();
				});
				timer();
				});

				$('#carousel_next').click(function(){
				clearInterval(setTimer);
				$('#carousel_move:not(:animated)').animate({left: '-=' + (listWidth)},slideTime,function(){
				carouselPosition();
				});
				timer();
				});

				function carouselPosition(){
				var ulLeft = parseInt($('#carousel_move').css('left'));
				var maskWidth = (carouselWidth) - ((listWidth)*(listCount));
				if(ulLeft == ((-(ulWidth))*2)) {
				$('#carousel_move').css({left:-(ulWidth)});
				} else if(ulLeft == 0) {
				$('#carousel_move').css({left:-(ulWidth)});
				};
				};

				timer();

				function timer() {
				setTimer = setInterval(function(){
				$('#carousel_next').click();
				},delayTime);
				};

				});
				});
			</script>

	
			<div id ="topic">
				<div id="carousel">
				<ul>
				<li><div id ="imgs">
					<a href ="artist.html"><img src="./img/c.png" alt = "photo" width = 110 height =150></a>
					</div>
					<!--<input type="text" class="focus" value="シャーリーズセロン　映画" />
					<input type ="submit" value ="検索">-->
					<h4><a href ="artist.html">シャーリーズセロン</a>が主演する映画のサントラをプロデュース!</h4>
					<!--<h6><a href ="cdshousai.html">この楽曲を見に行く→</h6><img src ="./img/3.png" id ="sc" width = 25 height =25></a>-->
					<p>南アフリカに生まれたシャーリーズ・セロンは16歳の時にモデルコンテストに優勝して、<br />イタリアに行きモデルとして活躍します。
					17歳の時にニューヨークに移ってバレエ・ダンサーを<br />、膝の怪我で挫折して、ロサンジェルスに移って女優</p><p class = "">
					<a href = "">読む>>></a></p></li>
				<li><div id ="imgs">
					<a href ="artist.html"><img src="./img/c.png" alt = "photo" width = 110 height =150></a>
					</div>
					<!--<input type="text" class="focus" value="シャーリーズセロン　映画" />
					<input type ="submit" value ="検索">-->
					<h4><a href ="artist.html">シャーリーズセロン</a>が主演する映画のサントラをプロデュース!</h4>
					<!--<h6><a href ="cdshousai.html">この楽曲を見に行く→</h6><img src ="./img/3.png" id ="sc" width = 25 height =25></a>-->
					<p>南アフリカに生まれたシャーリーズ・セロンは16歳の時にモデルコンテストに優勝して、<br />イタリアに行きモデルとして活躍します。
					17歳の時にニューヨークに移ってバレエ・ダンサーを<br />、膝の怪我で挫折して、ロサンジェルスに移って女優</p><p class = "">
					<a href = "">読む>>></a></p></li>
				<li><div id ="imgs">
					<a href ="artist.html"><img src="./img/c.png" alt = "photo" width = 110 height =150></a>
					</div>
					<!--<input type="text" class="focus" value="シャーリーズセロン　映画" />
					<input type ="submit" value ="検索">-->
					<h4><a href ="artist.html">シャーリーズセロン</a>が主演する映画のサントラをプロデュース!</h4>
					<!--<h6><a href ="cdshousai.html">この楽曲を見に行く→</h6><img src ="./img/3.png" id ="sc" width = 25 height =25></a>-->
					<p>南アフリカに生まれたシャーリーズ・セロンは16歳の時にモデルコンテストに優勝して、<br />イタリアに行きモデルとして活躍します。
					17歳の時にニューヨークに移ってバレエ・ダンサーを<br />、膝の怪我で挫折して、ロサンジェルスに移って女優</p><p class = "">
					<a href = "">読む>>></a></p></li>
				<li><div id ="imgs">
					<a href ="artist.html"><img src="./img/c.png" alt = "photo" width = 110 height =150></a>
					</div>
					<!--<input type="text" class="focus" value="シャーリーズセロン　映画" />
					<input type ="submit" value ="検索">-->
					<h4><a href ="artist.html">シャーリーズセロン</a>が主演する映画のサントラをプロデュース!</h4>
					<!--<h6><a href ="cdshousai.html">この楽曲を見に行く→</h6><img src ="./img/3.png" id ="sc" width = 25 height =25></a>-->
					<p>南アフリカに生まれたシャーリーズ・セロンは16歳の時にモデルコンテストに優勝して、<br />イタリアに行きモデルとして活躍します。
					17歳の時にニューヨークに移ってバレエ・ダンサーを<br />、膝の怪我で挫折して、ロサンジェルスに移って女優</p><p class = "">
					<a href = "">読む>>></a></p></li>
<li><div id ="imgs">
					<a href ="artist.html"><img src="./img/c.png" alt = "photo" width = 110 height =150></a>
					</div>
					<!--<input type="text" class="focus" value="シャーリーズセロン　映画" />
					<input type ="submit" value ="検索">-->
					<h4><a href ="artist.html">シャーリーズセロン</a>が主演する映画のサントラをプロデュース!</h4>
					<!--<h6><a href ="cdshousai.html">この楽曲を見に行く→</h6><img src ="./img/3.png" id ="sc" width = 25 height =25></a>-->
					<p>南アフリカに生まれたシャーリーズ・セロンは16歳の時にモデルコンテストに優勝して、<br />イタリアに行きモデルとして活躍します。
					17歳の時にニューヨークに移ってバレエ・ダンサーを<br />、膝の怪我で挫折して、ロサンジェルスに移って女優</p><p class = "">
					<a href = "">読む>>></a></p></li>
				<li><div id ="imgs">
					<a href ="artist.html"><img src="./img/c.png" alt = "photo" width = 110 height =150></a>
					</div>
					<!--<input type="text" class="focus" value="シャーリーズセロン　映画" />
					<input type ="submit" value ="検索">-->
					<h4><a href ="artist.html">シャーリーズセロン</a>が主演する映画のサントラをプロデュース!</h4>
					<!--<h6><a href ="cdshousai.html">この楽曲を見に行く→</h6><img src ="./img/3.png" id ="sc" width = 25 height =25></a>-->
					<p>南アフリカに生まれたシャーリーズ・セロンは16歳の時にモデルコンテストに優勝して、<br />イタリアに行きモデルとして活躍します。
					17歳の時にニューヨークに移ってバレエ・ダンサーを<br />、膝の怪我で挫折して、ロサンジェルスに移って女優</p><p class = "">
					<a href = "">読む>>></a></p></li>
				<li><div id ="imgs">
					<a href ="artist.html"><img src="./img/c.png" alt = "photo" width = 110 height =150></a>
					</div>
					<!--<input type="text" class="focus" value="シャーリーズセロン　映画" />
					<input type ="submit" value ="検索">-->
					<h4><a href ="artist.html">シャーリーズセロン</a>が主演する映画のサントラをプロデュース!</h4>
					<!--<h6><a href ="cdshousai.html">この楽曲を見に行く→</h6><img src ="./img/3.png" id ="sc" width = 25 height =25></a>-->
					<p>南アフリカに生まれたシャーリーズ・セロンは16歳の時にモデルコンテストに優勝して、<br />イタリアに行きモデルとして活躍します。
					17歳の時にニューヨークに移ってバレエ・ダンサーを<br />、膝の怪我で挫折して、ロサンジェルスに移って女優</p><p class = "">
					<a href = "">読む>>></a></p></li>
				<li><div id ="imgs">
					<a href ="artist.html"><img src="./img/c.png" alt = "photo" width = 110 height =150></a>
					</div>
					<!--<input type="text" class="focus" value="シャーリーズセロン　映画" />
					<input type ="submit" value ="検索">-->
					<h4><a href ="artist.html">シャーリーズセロン</a>が主演する映画のサントラをプロデュース!</h4>
					<!--<h6><a href ="cdshousai.html">この楽曲を見に行く→</h6><img src ="./img/3.png" id ="sc" width = 25 height =25></a>-->
					<p>南アフリカに生まれたシャーリーズ・セロンは16歳の時にモデルコンテストに優勝して、<br />イタリアに行きモデルとして活躍します。
					17歳の時にニューヨークに移ってバレエ・ダンサーを<br />、膝の怪我で挫折して、ロサンジェルスに移って女優</p><p class = "">
					<a href = "">読む>>></a></p></li>
				</ul>
			</div>
		</div>
		<div id ="tokushu">
			<a href ="tokushu.html"><p> >シーズンにあった曲特集</p></a>
			<a href ="tokushu.html"><p> >ドラマ曲</p></a>
			<a href ="tokushu.html"><p> >CM曲</p></a>
			<a href ="tokushu.html"><p> >年代シリーズ</p></a>
			<a href ="tokushu.html"><p> >カラオケランキング</p></a>
		</div>





			</div>
	
			
		
			
			<!--<div id ="rankin_all">
				<center>全体の楽曲のランキング</center>
				<div id ="rankin_list">
					<ul>
				<li id ="#"><a href ="genre.html">片想いFinally　　　　　　　　　SKE48</a></li>
				<li id ="#"><a href ="genre.html">ナイショの話　　　　　　　　　　ClariS</a></li>
				<li id ="#"><a href ="genre.html">ひとつ　　　　　　　　　　　　　長渕剛</a></li>
				<li id ="#"><a href ="genre.html">ワールド　　　　　　　　　　　 CNBLUE</a></li>
				<li id ="#"><a href ="genre.html">Where you are　　　　　　　　SuG</a></li>
				<li id ="#"><a href ="genre.html">ロック　　　　　　　　　　　　 スマイレージ</a></li>
				<li id ="#"><a href ="genre.html">チョトマテクダサイ！　　　　　スマイレージ</a></li>
				<li id ="#"><a href ="genre.html">ダンス.ハウス　　　　　　　　　azuma</a></li>
				<li id ="#"><a href ="genre.html">満月に吠えろ　　　　　　　　　チャットモンチー</a></li>
				<li id ="#"><a href ="genre.html">いのちの歌　　　　　　　　　　竹内まりや</a></li>
				<li id ="#"><a href ="genre.html">クラシック邦　　　　　　　　　川田真美</a></li>
				<li id ="#"><a href ="genre.html">Serment　　　　　　　　　　　JUJU</a></li>
				</ul>	
			</div>
			<center>10位以下</center>
		</div>-->
		
		
		
		
		
		
		
		
		
		
		<!--カルーセル
		    <script type="text/javascript">
           (function(promo) {
             var promoContent = promo.find(".promo-content");
             var items = promoContent.children();
             items.each(function(i, n) {
               var href = $(n).find("a").attr("href");
               $(n).click(function() { location.href = href; });
             });
             var pageIndicators = [];
             var width = promo.width();
             var pageIndicatorMinSize = 8;
             var pageIndicatorMaxSize = 16;
             var pageIndicatorInterval = 24;
             var x = width - pageIndicatorInterval * items.length;
             var ox = 0;
             for (var i = 0; i < items.length; i++) {
               var pageIndicator = {
                 sx: i * width,
                 x: x,
                 size: pageIndicatorMinSize,
                 n: $('<span>●</span>')
                   .css('cursor', 'pointer')
                   .addClass("promo-page-indicator")
                   .addClass("promo-page-indicator-" + i)
                   .appendTo(promo),
                 refresh: function() {
                   var d = this.sx - ox;
                   size = Math.ma
                     pageIndicatorMaxSize * Math.exp(-(d * d) / (width * width)),
                     pageIndicatorMinSize) | 0;
                   this.n.css({
                     width: size + "px",
                     fontSize: size + "px",
                     left: ox + ((this.x - size / 2) | 0) + "px"
                   });
                 }
               };
               pageIndicators[i] = pageIndicator;
               pageIndicator.refresh();
               x += pageIndicatorInterval;
             }
             function moveTo(x) {
               ox = x;
               for (var i = 0; i < items.length; i++) {
                 pageIndicators[i].refresh();
               }
               promo[0].scrollLeft = x;
             }
             x = 0;
             var animating = false;
             function easing(from, to, s, f, c) {
               if (animating)
                 return;
               var v = from;
               animating = true;
               var t = setInterval(function() {
                 f(v);
                 v += (to - v) / 10;
                 if ((to > from && to - v < 1) || (to <= from && v - to < 1)) {
                   animating = false;
                   clearInterval(t);
                   c();
                 }
               }, s);
             }
             $(function() {
               var n = 0;
               for (var i = 0; i < items.length; i++) {
                 (function(i) {
                   pageIndicators[i].n.click(function() {
                     easing(n * width, i * width, 20, moveTo, function() {});
                   });
                 })(i);
               }
               function next() {
                 setTimeout(function() {
                   if (n + 1 >= items.length) {
                     easing(n * width, 0, 20, moveTo, next);
                     n = 0;
                   } else {
                     easing(n * width, (n + 1) * width, 20, moveTo, next);
                     n++;
                   }
                 }, 3300);
               }
               next();
             });
           })($(".promo"));
         </script>
		 
		 
		 
		 
		 
		 
		 
		 
		 
		
		
		  <div class="promo">
           <ul class="promo-content">
             <li class="without_description first">
               <a href="http://ticket.rakuten.co.jp/static/features/tokyo-runway/"><img src="http://rakuten-ticket-static.s3-ap-northeast-1.amazonaws.com/images/uploaded/e909d53d-992f-4b78-befb-da6d5d659d03.jpg" /></a>
               <div class="band">&nbsp;</div>
               <div class="title"><a href="http://ticket.rakuten.co.jp/static/features/tokyo-runway/">東京ランウェイ 2012 Spring/Summer</a></div>
             </li>
                                                                     
<li class="without_description">
               <a href="http://ticket.rakuten.co.jp/static/features/blueman/"><img src="http://rakuten-ticket-static.s3-ap-northeast-1.amazonaws.com/images/uploaded/cbcbe678-52fe-4b42-a14c-defe3856a720.jpg" /></a>
               <div class="band">&nbsp;</div>
               <div class="title"><a href="http://ticket.rakuten.co.jp/static/features/blueman/">ブルーマングループ IN 東京</a></div>
             </li>
                                                                    
 <li class="without_description">
               <a href="http://ticket.rakuten.co.jp/s/%E9%9F%B3%E6%A5%BD/THE+TOUR+OF+MISIA+JAPAN+SOUL+QUEST+GRAND+FINALE+2012/!DGATM"><img src="http://rakuten-ticket-static.s3-ap-northeast-1.amazonaws.com/images/uploaded/e541b3ad-8b7f-4a9d-8608-d1a012f41527.jpg" /></a>
               <div class="band">&nbsp;</div>
               <div class="title"><a href="http://ticket.rakuten.co.jp/s/%E9%9F%B3%E6%A5%BD/THE+TOUR+OF+MISIA+JAPAN+SOUL+QUEST+GRAND+FINALE+2012/!DGATM">THE TOUR OF MISIA JAPAN SOUL QUEST GRAND FINALE 2012</a></div>
             </li>
                                                                     
<li class="without_description last">
               <a href="http://ticket.rakuten.co.jp/static/features/kooza/"><img src="http://rakuten-ticket-static.s3-ap-northeast-1.amazonaws.com/images/uploaded/3f031a09-5b5e-4c5e-8b58-7d47cfab01c7.jpg" /></a>
               <div class="band">&nbsp;</div>
               <div class="title"><a href="http://ticket.rakuten.co.jp/static/features/kooza/">ダイハツ  クーザ 福岡公演 </a></div>
             </li>
           </ul>
         </div>



		カルーセル-->
		
	</div>		

	<div id = "tx_right">
		邦楽ランキング
	<table>
     <tr>
          <td>1位　　　　*******</td>
     </tr>
     <tr>
          <td>2位　　　　*******</td>
     </tr>
     <tr>
          <td>3位　　　　********</td>
     </tr>
     <tr>
          <td>4位　　　　********</td>
     </tr>
	 <tr>
          <td>5位　　　　********</td>
     </tr>
	 <tr>
          <td>6位　　　　********</td>
     </tr>
	 <tr>
          <td>7位　　　　********</td>
     </tr>
	 <tr>
          <td>8位　　　　********</td>
     </tr>
	  <tr>
          <td>9位　　　　********</td>
     </tr>
	  <tr>
          <td>10位　　　　********</td>
     </tr>
</table>
		洋楽ランキング
	<table>
     <tr>
          <td>1位　　　　*******</td>
     </tr>
     <tr>
          <td>2位　　　　*******</td>
     </tr>
     <tr>
          <td>3位　　　　********</td>
     </tr>
     <tr>
          <td>4位　　　　********</td>
     </tr>
	 <tr>
          <td>5位　　　　********</td>
     </tr>
	 <tr>
          <td>6位　　　　********</td>
     </tr>
	 <tr>
          <td>7位　　　　********</td>
     </tr>
	 <tr>
          <td>8位　　　　********</td>
     </tr>
	  <tr>
          <td>9位　　　　********</td>
     </tr>
	  <tr>
          <td>10位　　　　********</td>
     </tr>
</table>


<script type ="text/javascript">
$(function(){
     $("tr:odd").addClass("odd");
	 $("tr:first").addClass("fir");
});
</script>


		</div>
		<!--芸能人のツイッター　日替わり？
		<script charset="utf-8" src="http://widgets.twimg.com/j/2/widget.js"></script>
<script>
new TWTR.Widget({
  version: 2,
  type: 'profile',
  rpp: 8,
  interval: 30000,
  width: 170,
  height: 300,
  theme: {
    shell: {
      background: '#31def5',
      color: '#ffffff'
    },
    tweets: {
      background: '#fafafa',
      color: '#050505',
      links: '#3b30d9'
    }
  },
  features: {
    scrollbar: false,
    loop: false,
    live: true,
    behavior: 'all'
  }
}).render().setUser('katosaori').start();
</script>


-->

	</div>
	</div>
			<!--<div id="footer">
			<div id ="continer">
				<ul>
					<li>
						<a href="">運営について</a>
					</li>
					<li>
						<a href="">ヘルプ</a>
					</li>
					<li>
						<a href="">求人</a>
					</li>
					<li>
						<a href="">規約</a>
					</li>
					<li>
						<a href="">プライバシー</a>
					</li>
					<li>
						<span id="copyright">&copy;2011 ####.</span>
					</li>
				</ul>
			</div>-->
</div>
</body>
</html>
?>
