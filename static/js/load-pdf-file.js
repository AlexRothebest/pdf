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

$(document).ready(function(){
	$('#pdf-file-input').change(function() {
		$('#uploaded-files-hint').text($('#pdf-file-input').prop('files').length + ' file(s) uploaded');
	});

	$('#load-file-btn').click(function(){
		var files = $('#pdf-file-input').prop('files'),
			fd = new FormData;

		for (let fileNum in files) {
			fd.append('pdf-file', files[fileNum]);
		}

		$('#result-field').text('Parsing in process...');
		$('#results-saved-msg').hide();
		$.ajax({
			url: '/api/parse-pdf',
			type: 'POST',
			async: true,
			data: fd,
			processData: false,
			contentType: false,
			headers: {
				'X-CSRFToken': getCookie('csrftoken')
			},
			success: function(result){
				$('#result-field').text(result.message);
				$('#results-saved-msg').show();
				$('#google-sheet-link').attr('href', 'https://docs.google.com/spreadsheets/d/' + result['google_sheet_id'] + '/edit#gid=0');
			},
			error: function(){
				alert('Error in AJAX((99(((((99((');
			}
		});
	});
});