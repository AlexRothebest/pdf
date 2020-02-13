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
				allInputs = $('input'),
			dataValid = true,
			isValid = true;

		if ($('select').length != 0) {
			var status = $('#status_field').val();
		} else {
			var status = 'user';
		}

		for (let i = 1; i < allInputs.length; i++) {
			let id = $('input').get(i).id;
			isValid = valid(id);
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
				try {
					var googleSheetId = $('#google-sheet-id').val().split('/spreadsheets/d/')[1].split('/')[0];
				} catch {
					$('input#google-sheet-id').css('border-color', 'red');
					$('#error_msg_container').text('Wrong link');
					$('#error_msg_container').show();
					return;
				}

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

				$.ajax({
					type: 'POST',
					async: true,
					url: '/api/add-user/',
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
				});
			}
		}
	});
});