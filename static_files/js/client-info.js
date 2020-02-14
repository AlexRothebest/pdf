function getCookie(name) {
	var cookieValue = null;
	if (document.cookie && document.cookie !== '') {
		var cookies = document.cookie.split(';');
		for (var i = 0; i < cookies.length; i++) {
			var cookie = cookies[i].trim();
			if (cookie.substring(0, name.length + 1) === (name + '=')) {
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
			}
		}
	}
	return cookieValue;
}


if (!Array.prototype.last) {
	Array.prototype.last = function() {
		return this[this.length - 1];
	}
}


$(document).ready(function() {
	$('#save-btn').click(function() {
		var newStatus = $("input[name='client-status']:checked").val(),
			clientId = location.href.split('/').last(),
			ajaxData = {};

		ajaxData[clientId] = newStatus;

		$.ajax({
			url: '/api/change-clients-data',
			type: 'POST',
			async: true,
			data: ajaxData,
			headers: {
				'X-CSRFToken': getCookie('csrftoken')
			},
			success: function() {
				location.replace('');
			},
			error: function(){
				alert('Error in AJAX((99(((((99((');
			}
		});
	});

	$("input[name='client-status']").click(function() {
		$('#save-btn').show();
	});
});