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
	var newStatuses = {};

	$('.client-status-input').click(function() {
		newStatuses[$(this).attr('client-id')] = $(this).val();
		$('#save-btn').show();
	});

	$('#search-input').keyup(function() {
		var searchText = $(this).val().trim(),
			clientBlocks = $('.client-info-block'),
			inText;

		// alert($('.client-info-block').length);
		for (let clientBlock of clientBlocks) {
			inText = ($(clientBlock).find('.name').text() + $(clientBlock).find('.email').text() + $(clientBlock).find('.username').text()).toLowerCase();
			// alert(inText);
			if (inText == '' || inText.indexOf(searchText) == -1) {
				$(clientBlock).hide();
			} else {
				$(clientBlock).show();
			}
		}
	});


	$('#save-btn').click(function() {
		var ajaxData = newStatuses;

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
});