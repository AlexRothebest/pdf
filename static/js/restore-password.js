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
		url: '/api/restore_password/',
		data: data,
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