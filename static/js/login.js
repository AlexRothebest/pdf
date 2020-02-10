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

function authenticateUser() {
	var username = $('#username_field').val(),
		password = $('#password_field').val();

	var data = {username: username, password: password};

	$('#processing_login').show();
	$('#forgot_password_msg').css({'visibility': 'hidden'});
	$('#login_error').hide();

	$.ajax({
		type: 'POST',
		async: true,
		url: '/api/login/',
		data: data,
		headers: {
			'X-CSRFToken': getCookie('csrftoken')
		},
		success: function(result) {
			$('#processing_login').hide();
			$('#forgot_password_msg').css({'visibility': 'visible'});
			if (result.status == 'accepted') {
				location.replace('/');
			} else {
				$('#error_msg_container').text(result.message);
				$('#error_msg_container').show();
			}
		},
		error: function() {
			alert('Error in AJAX((99(((((99((');
		}
	});
}

$(document).ready(function () {
	$('#register_button').click(authenticateUser);
	$('input').keyup(function(e) {
		if (e.keyCode == 13) {
			authenticateUser();
		}
	});
});