<%block name="countdown">
		<dl id="sideCountDown">
			<dt>公演終了まで</dt>
			<dd><span>14</span>日</dd>
		</dl>
</%block>
<%block name="facebook">
		<iframe src="//www.facebook.com/plugins/likebox.php?href=http%3A%2F%2Fwww.facebook.com%2Fpages%2F%25E3%2583%2596%25E3%2583%25AB%25E3%2583%25BC%25E3%2583%259E%25E3%2583%25B3%2F210488268963686&amp;width=240&amp;height=290&amp;colorscheme=light&amp;show_faces=true&amp;border_color&amp;stream=false&amp;header=true" scrolling="No" frameborder="0" style="border:none; overflow:hidden; width:240px; height:290px;" allowtransparency="true"></iframe>
</%block>
<%block name="twitter">
		<script charset="utf-8" src="http://widgets.twimg.com/j/2/widget.js"></script>
		<script>
		new TWTR.Widget({
		  version: 2,
		  type: 'search',
		  search: 'ブルーマン',
		  interval: 30000,
		  title: 'ブルーマン IN 東京',
		  subject: 'ブルーマンについてのtweet',
		  width: 240,
		  height: 500,
		  theme: {
			shell: {
			  background: '#f2f2e5',
			  color: '#000000'
			},
			tweets: {
			  background: '#ffffff',
			  color: '#444444',
			  links: '#1985b5'
			}
		  },
		  features: {
			scrollbar: false,
			loop: true,
			live: true,
			behavior: 'default'
		  }
		}).render().start();
		</script>
</%block>
