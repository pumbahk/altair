## twitter widget output template
## 
<style type="text/css">
  .twitter-widget h2 {
    background: none;
  }
  .twitter-widget h3 {
    background: none;
  }
  .twitter-widget h4 {
    background: none;
  }
</style>
<div class="twitter-widget">
  <script charset="utf-8" src="http://widgets.twimg.com/j/2/widget.js"></script>
  <script>
  new TWTR.Widget({
	version: 2,
	type: 'search',
	search: '${widget.search_query}',
	interval: 30000,
	title: '${widget.title}',
	subject: '${widget.subject}',
	width: 250,
	height: 300,
	theme: {
	  shell: {
		background: '#8ec1da',
		color: '#ffffff'
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
</div>
