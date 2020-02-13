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
	let newStatuses = {},
		selectedClientsIds = [];

	$('#search-input').keyup(function() {
		let searchText = $(this).val().trim(),
			clientBlocks = $('.client-info-block'),
			inText;

		for (let clientBlock of clientBlocks) {
			inText = ($(clientBlock).find('.name').text() + $(clientBlock).find('.email').text() + $(clientBlock).find('.username').text()).toLowerCase();
			if (inText == '' || inText.indexOf(searchText) == -1) {
				$(clientBlock).hide();
			} else {
				$(clientBlock).show();
			}
		}
	});



	$('.client-status-input').click(function() {
		newStatuses[$(this).parent().parent().parent().attr('client-id')] = $(this).val();
		$('#save-btn').show();
	});


	$('#save-btn').click(function() {
		let ajaxData = newStatuses;

		$.ajax({
			url: '/api/change-clients-data',
			type: 'POST',
			async: true,
			data: ajaxData,
			headers: {
				'X-CSRFToken': getCookie('csrftoken')
			},
			success: function() {
				location.replace('');
			},
			error: function(){
				alert('Error in AJAX((99(((((99((');
			}
		});
	});



	$('.name, .username').click(function() {
		let clientInfoURL = '/admin/client/' + $(this).parent().attr('client-id');
		window.open(clientInfoURL, '_blank')
	});



	$('.id').click(function() {
		let clientId = $(this).parent().attr('client-id');
		if (selectedClientsIds.indexOf(clientId) == -1) {
			selectedClientsIds.push(clientId);
			$(this).parent().children().css({'background-color': '#66ff99'});
		} else {
			selectedClientsIds.splice(selectedClientsIds.indexOf(clientId), 1);
			$('table tr:nth-child(odd) td').css({'background-color': '#eaeae1'});
			$('table tr:nth-child(even) td').css({'background-color': 'white'});
			for (clientId of selectedClientsIds) {
				$("tr[client-id='" + clientId + "']").children().css({'background-color': '#66ff99'});
			}
		}

		if (selectedClientsIds.length > 0) {
			$('#delete-clients-btn').show();
			$('#load-clients-data-btn').show();
		} else {
			$('#delete-clients-btn').hide();
			$('#load-clients-data-btn').hide();
		}
	});



	$('#delete-clients-btn').click(function() {
		let ajaxData = {
			clientsToDelete: selectedClientsIds.join(', ')
		};

		$.ajax({
			url: '/api/delete-clients',
			type: 'POST',
			async: true,
			data: ajaxData,
			headers: {
				'X-CSRFToken': getCookie('csrftoken')
			},
			success: function() {
				location.replace('');
			},
			error: function(){
				alert('Error in AJAX((99(((((99((');
			}
		});
	});


	$('#load-clients-data-btn').click(function() {
		let ajaxData = {
			clientsToDownload: selectedClientsIds.join(', ')
		};

		$.ajax({
			url: '/api/download-clients-parsed-data',
			type: 'POST',
			async: true,
			data: ajaxData,
			xhrFields: {
				responseType: 'blob'
			},
			headers: {
				'X-CSRFToken': getCookie('csrftoken')
			},
			success: function(data) {
				var a = document.createElement('a');
				var url = window.URL.createObjectURL(data);
				a.href = url;
				a.download = 'Data.xls';
				document.body.append(a);
				a.click();
				a.remove();
				window.URL.revokeObjectURL(url);
			},
			error: function(){
				alert('Error in AJAX((99(((((99((');
			}
		});
	});
});