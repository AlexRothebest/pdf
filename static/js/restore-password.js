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
	$('#wait_msg1').hide();
	$('#wait_msg2').hide();
	$('#email_sent_msg1').hide();
	$('#email_sent_msg2').hide();
	$('#wrong_username_msg').hide();
	$('#wrong_email_msg').hide();
}
function sendMail(field) {
	eval("var data = {" + field + ": $('#' + field + '_field').val()};");

	alert(data.username);

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
		success: function(success) {
			hideAllMsg();
			if (success) {
				if (field == 'username') {
					$('#email_sent_msg1').show();
				} else {
					$('#email_sent_msg2').show();
				}
				setTimeout(function() {location.replace('/login/')}, 5000);
			} else {
				if (field == 'username') {
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