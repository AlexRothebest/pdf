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

$(document).ready(function() {
	$('#register_button').click(function() {
		function valid(inputFieldId) {
			let inputField = $('#' + inputFieldId);
			if (inputField.is(':valid') == false) {
				inputField.css('border-color', 'red');
				return false;
			} else {
				inputField.css('border-color', 'black');
				return true;
			}
		}

		var name = $('#name_field').val(),
			surname = $('#surname_field').val(),
			email = $('#email_field').val(),
			username = $('#username_field').val(),
			password = $('#password_field').val(),
			repeatPassword = $('#repeat_password_field').val(),
			googleSheetId = $('#google-sheet-id').val().split('/spreadsheets/d/')[1].split('/')[0],
			allInputs = $('input'),
			dataValid = true,
			isValid = true;

		if ($('select').length != 0) {
			var status = $('#status_field').val();
		} else {
			var status = 'user';
		}

		for (let i = 0; i < allInputs.length - 1; i++) {
			isValid = valid(allInputs[i].id);
			dataValid = dataValid && isValid;
		}

		if (dataValid == false) {
			$('#validation_error_msg').show();
		} else {
			$('#validation_error_msg').hide();
			if (password != repeatPassword) {
				$('#passwords_dont_match_error_msg').show();
				$('#password_field').css('border-color', 'red');
				$('#repeat_password_field').css('border-color', 'red');
			} else {
				$('#passwords_dont_match_error_msg').hide();
				$('#wait_msg').show()
				var data = {
					name: name,
					surname: surname,
					email: email,
					status: status,
					username: username,
					password: password,
					'google-sheet-id': googleSheetId
				}

				// alert('AJAX will be executed now');

				$.ajax({
					type: 'POST',
					async: true,
					url: '/api/add_user/',
					data: data,
					headers: {
						'X-CSRFToken': getCookie('csrftoken')
					},
					success: function(result) {
						$('#wait_msg').hide();
						if (result.status == 'accepted') {
							location.replace('/');
						} else {
							$('#error_msg_container').text(result.message);
							$('#error_msg_container').show();
						}
					},
					error: function() {
						alert('Error in AJAX((99(((((99((');
						$('#wait_msg').hide();
					}
				})
			}
		}
	})
});