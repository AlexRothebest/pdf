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

function registerUser() {
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

	$('input').css('border-color', 'black');
	var name = $('#name_field').val(),
		surname = $('#surname_field').val(),
		email = $('#email_field').val(),
		username = $('#username_field').val(),
		password = $('#password_field').val(),
		repeatPassword = $('#repeat_password_field').val(),
		allInputs = $('input'),
		dataValid = true,
		isValid = true;

	for (let i = 1; i < allInputs.length; i++) {
		let id = $('input').get(i).id;
		isValid = valid(id);
		dataValid = dataValid && isValid;
	}

	if (dataValid == false) {
		$('#error_msg_container').text('Please fill in all fields correctly');
		$('#error_msg_container').show();
	} else {
		if (password != repeatPassword) {
			$('#error_msg_container').text("Passwords don't macth");
			$('#error_msg_container').show();
			$('#password_field, #repeat_password_field').css('border-color', 'red');
		} else {
			try {
				var googleSheetId = $('#google-sheet-id').val().split('/spreadsheets/d/')[1].split('/')[0];
			} catch {
				$('input#google-sheet-id').css('border-color', 'red');
				$('#error_msg_container').text('Wrong link');
				$('#error_msg_container').show();
				return;
			}

			$('#error_msg_container').hide();
			$('#wait_msg').show()

			var data = {
				name: name,
				surname: surname,
				email: email,
				status: 'user',
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
					$('#wait_msg').hide();
					alert('Error in AJAX((99(((((99((');
				}
			});
		}
	}
}

$(document).ready(function () {
	$('#register_button').click(registerUser);
	$('input').keyup(function(e) {
		if (e.keyCode == 13) {
			registerUser();
		}
	});
});