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


function hideAllMsg() {
	$(`#wait_msg1,
	   #wait_msg2,
	   #email_sent_msg1,
	   #email_sent_msg2,
	   #wrong_username_msg,
	   #wrong_email_msg`).hide();
}


function restorePassword(field) {
	eval("var data = {" + field + ": $('#' + field + '-field').val()};");

	hideAllMsg();

	if (field == 'username') {
		$('#wait_msg1').show();
	} else {
		$('#wait_msg2').show();
	}

	$.ajax({
		type: 'POST',
		async: true,
		url: '/api/restore-password',
		data: data,
		headers: {
			'X-CSRFToken': getCookie('csrftoken')
		},
		success: function(result) {
			hideAllMsg();
			if (result.status == 'Accepted') {
				if (field == 'username') {
					$('#email_sent_msg1').show();
				} else {
					$('#email_sent_msg2').show();
				}
				// setTimeout(function() {location.replace('/login/')}, 5000);
			} else {
				if (result.message == 'Usename does not exist') {
					$('#wrong_username_msg').show();
				} else {
					$('#wrong_email_msg').show();
				}
			}
		},
		error: function() {
			hideAllMsg();
			alert('Error in AJAX((99(((((99((');
		}
	});
}


$(document).ready(function () {
	$('#restore-by-username-btn').click(function() {
		restorePassword('username');
	});

	$('#username-field').keyup(function(e) {
		if (e.keyCode == 13) {
			restorePassword('username');
		}
	});


	$('#restore-by-email-btn').click(function() {
		restorePassword('email');
	});

	$('#email-field').keyup(function(e) {
		if (e.keyCode == 13) {
			restorePassword('email');
		}
	});
});