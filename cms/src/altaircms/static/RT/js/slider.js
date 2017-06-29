$(function() {
	$('#full-carousel').carouFredSel({
		width: '100%',
		items: {
			visible: 3,
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



(function() {
	function image_class() {
		var img = new Image();
		var images = document.querySelectorAll('img');
		for (var i = 0; i < images.length; i++) {
			img.src = images[i].src;
			if (img.width < img.height) {
				images[i].className += ' vertically_long';
				images[i].parentNode.className += ' vertically_long_outer';
			} else if (img.width > img.height) {
				images[i].className += ' horizontally_long';
				images[i].parentNode.className += ' horizontally_long_outer';
			} else {
				images[i].className += ' square';
				images[i].parentNode.className += ' square_outer';
			}
		}
	}
	if (window.addEventListener) {
		window.addEventListener('load', image_class, false);
	} else if (window.attachEvent) {
		window.attachEvent('onload', image_class);
	}
})();