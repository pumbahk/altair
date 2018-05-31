$(function () {
	var topBtn = $("#seach_btn");
	topBtn.hide();
	$(window).scroll(function () {
		if ($(this).scrollTop() > 300) {
			topBtn.fadeIn(2000);
		} else {
			topBtn.fadeOut(1000);
		}
	});
});








