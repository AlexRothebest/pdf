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
		$('#uploaded-files-hint').text($('#pdf-file-input').prop('files').length + ' file(s) are uploaded');
	});


	$('#load-file-btn').click(function(){
		var files = $('#pdf-file-input').prop('files'),
			fd = new FormData,
			nextRowToWriteData = parseInt($('#next-row-to-write-data-field').val()),
			googlesheetId = $('#select-google-sheet-field').val();


		if (isNaN(nextRowToWriteData)) {
			nextRowToWriteData = 3
		}

		$('#next-row-to-write-data-field').val(nextRowToWriteData);


		for (let fileNum in files) {
			fd.append('pdf-file', files[fileNum]);

			if (fileNum == '9') {
				break;
			}
		}


		$('#result-field').text('Scanning files...');
		$('#results-saved-msg').hide();

		$('#parsed-files, #error-files').empty();

		$('#parsed-files-block, #error-files-block').hide();


		$.ajax({
			url: '/api/parse-pdf',
			type: 'POST',
			async: true,
			data: fd,
			processData: false,
			contentType: false,
			headers: {
				'X-CSRFToken': getCookie('csrftoken'),
				nextRowToWriteData: nextRowToWriteData,
				googlesheetId: googlesheetId
			},
			success: function(result){
				$('#result-field').text(result.message);
				$('#results-saved-msg').show();

				$('#google-sheet-link').attr('href', 'https://docs.google.com/spreadsheets/d/' + result.google_sheet_id + '/edit#gid=0');

				$('#next-row-to-write-data-field').val(result.next_row_to_write_data);


				console.log(result.parsed_filenames);

				for (parsedFileName in result.parsed_filenames) {
					$('#parsed-files').append(
						$('<li></li>').append(
							$('<a></a>').text(parsedFileName).attr(
								{
									'href': result.parsed_filenames[parsedFileName],
									'target': '_blank'
								}
							)
						)
					);

					$('#parsed-files-block').show();
				}

				for (errorFileName in result.error_filenames) {
					$('#error-files').append(
						$('<li></li>').append(
							$('<a></a>').text(errorFileName).attr(
								{
									'href': result.error_filenames[errorFileName],
									'target': '_blank'
								}
							)
						)
					);

					$('#error-files-block').show();
				}
			},
			error: function(){
				alert('Error in AJAX((99(((((99((');
			}
		});
	});


	let maxRow = 0;
	for (let sheetData of googleSheetsData) {
		if (sheetData.nextRow > maxRow) {
			$('#select-google-sheet-field').val(sheetData.id);
			$('#next-row-to-write-data-field').val(sheetData.nextRow);

			$('#googlesheet-link').attr({
				'href': 'https://docs.google.com/spreadsheets/d/' + sheetData.id + '/edit#gid=0'
			})

			maxRow = sheetData.nextRow;
		}
	}


	$('#select-google-sheet-field').change(function() {
		let selectedSheetId = $(this).val();

		for (let sheetData of googleSheetsData) {
			if (sheetData.id == selectedSheetId) {
				$('#next-row-to-write-data-field').val(sheetData.nextRow);

				break;
			}
		}

		$('#googlesheet-link').attr({
			'href': 'https://docs.google.com/spreadsheets/d/' + selectedSheetId + '/edit#gid=0'
		})
	});
});