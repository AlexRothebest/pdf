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


function changePassword() {
	let oldPassword = $('#old-password-field').val(),
		newPassword = $('#new-password-field').val(),
		repeatNewPassword = $('#repeat-new-password-field').val();


	$('#wrong-password-msg').css({
		'visibility': 'hidden'
	});

	$('#passwords-dont-match-error-msg').css({
			'visibility': 'hidden'
		});

	$(`#new-password-field,
	   #repeat-new-password-field`).css({
		'border-color': 'black'
	});

	$('#wait-msg').show();


	if (newPassword != repeatNewPassword) {
		$('#wait-msg').hide();


		$(`#new-password-field,
		   #repeat-new-password-field`).css({
			'border-color': 'red'
		});

		$('#passwords-dont-match-error-msg').css({
			'visibility': 'visible'
		});


		return;
	}


	$.ajax({
		url: '/api/change-password',
		method: 'POST',
		async: true,
		data: {
			oldPassword: oldPassword,
			newPassword: newPassword
		},
		headers: {
			'X-CSRFToken': getCookie('csrftoken')
		},
		success: function(result) {
			if (result.status == 'Accepted') {
				$('#wait-msg').hide();

				location.href = '/';
			} else {
				if (result.message == 'Wrong password') {
					$('#wait-msg').hide();

					$('#wrong-password-msg').css({
						'visibility': 'visible'
					});
				}
			}
		},
		error: function() {
			alert('Error in AJAX((99(((((99((');
			$('#wait_msg').hide();
		}
	});
}


$(document).ready(function() {
	$('#change-password').click(changePassword);

	$('input').keyup(function(e) {
		if (e.keyCode == 13) {
			changePassword();
		}
	});
});