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


var existingLinkErrorText = 'You have already registered this googlesheet',
	wrongLinkErrorText = 'This is not a link to the googlesheet',
	notPreparedSheetErrorText = 'Looks like you haven\'t prepared your googlesheet correctly. Please follow the instructions',

	existingNameErrorText = 'You have already registered the googlesheet with the same name',
	emptyNameErrorText = 'Name of the googlesheet mustn\'t be empty';


function registerTheGoogleSheet() {
	let linkToTheGoogleSheet = $('#link-to-the-google-sheet-field').val().trim(),
		nameOfTheGoogleSheet = $('#name-of-the-google-sheet-field').val().trim();


	$(`#name-of-the-google-sheet-field,
	   #link-to-the-google-sheet-field`).css({
		'border-color': 'black'
	});

	$(`#link-error-msg,
	   #name-error-msg`).css({
		'visibility': 'hidden'
	});

	$('#wait-msg').show();


	try {
		linkToTheGoogleSheet = linkToTheGoogleSheet.split('/spreadsheets/d/')[1].split('/')[0];
	} catch {
		$('#link-to-the-google-sheet-field').css({
			'border-color': 'red'
		});


		$('#link-error-msg').text(wrongLinkErrorText);

		$('#link-error-msg').css({
			'visibility': 'visible'
		});


		$('#wait-msg').hide();


		return;
	}


	if (nameOfTheGoogleSheet == '') {
		$('#name-of-the-google-sheet-field').css({
			'border-color': 'red'
		});


		$('#name-error-msg').text(emptyNameErrorText);

		$('#name-error-msg').css({
			'visibility': 'visible'
		});


		$('#wait-msg').hide();


		return;
	}


	$.ajax({
		url: '/api/add-new-googlesheet',
		method: 'POST',
		async: true,
		data: {
			nameOfTheGoogleSheet: nameOfTheGoogleSheet,
			linkToTheGoogleSheet: linkToTheGoogleSheet
		},
		headers: {
			'X-CSRFToken': getCookie('csrftoken')
		},
		success: function(result) {
			$('#wait-msg').hide();

			if (result.status == 'Accepted') {
				location.href = '/';
			} else {
				if (result.message == 'Existing link') {
					$('#link-to-the-google-sheet-field').css({
						'border-color': 'red'
					});


					$('#link-error-msg').text(existingLinkErrorText);

					$('#link-error-msg').css({
						'visibility': 'visible'
					});
				} else if (result.message == 'Not prepared googlesheet') {
					$('#link-to-the-google-sheet-field').css({
						'border-color': 'red'
					});


					$('#link-error-msg').text(notPreparedSheetErrorText);

					$('#link-error-msg').css({
						'visibility': 'visible'
					});
				} else if (result.message == 'Existing name') {
					$('#name-of-the-google-sheet-field').css({
						'border-color': 'red'
					});


					$('#name-error-msg').text(existingNameErrorText);

					$('#name-error-msg').css({
						'visibility': 'visible'
					});
				}
			}
		},
		error: function() {
			alert('Error in AJAX((99(((((99((');

			$('#wait-msg').hide();
		}
	});
}


$(document).ready(function() {
	$('#register-btn').click(registerTheGoogleSheet);
});