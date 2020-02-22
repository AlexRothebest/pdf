from django.shortcuts import render, redirect
from django.template.context_processors import csrf

from main.models import Client


def get_username_and_status(request):
	args = {
		'client': Client.objects.get(account=request.user)
	}

	args.update(csrf(request))

	return args


def home(request):
	if request.user.is_authenticated:
		client = Client.objects.get(account=request.user)

		if client.status != 'a':
			return redirect('/')

		args = get_username_and_status(request)
		args['all_clients'] = Client.objects.all()

		return render(request, 'myadmin/index.html', args)
	else:
		return redirect('/')


def client_info(request, client_id):
	if request.user.is_authenticated:
		client = Client.objects.get(account=request.user)

		if client.status != 'a':
			return redirect('/')

		args = get_username_and_status(request)
		args['client_info'] = Client.objects.get(id=client_id)

		return render(request, 'myadmin/client-info.html', args)
	else:
		return redirect('/')