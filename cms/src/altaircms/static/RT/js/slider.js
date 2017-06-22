$(function() {
	$('#full-carousel').carouFredSel({
		width: '100%',
		items: {
			visible: 5,
			start: -1
		},
		scroll: {
			items: 1,
			duration: 800,
			timeoutDuration: 3000
		},
		prev: '#full-prev',
		next: '#full-next',
		pagination: {
			container: '#full-pager',
			deviation: 1
		}
	});
});