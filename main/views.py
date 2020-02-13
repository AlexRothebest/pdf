from django.shortcuts import render, redirect
from django.template.context_processors import csrf

from .models import Client


def get_username_and_status(request):
	client = Client.objects.get(account=request.user)

	args = {
		'username': request.user.username,
		'status': client.status,
		'client': client
	}
	args.update(csrf(request))

	return args


def home(request):
	return redirect('/login/')


def login(request):
	if not request.user.is_authenticated:
		args = {}
		args.update(csrf(request))

		return render(request, 'main/login.html', args)
	else:
		return redirect('/load-pdf/')


def add_user(request):
	if request.user.is_authenticated:
		args = get_username_and_status(request)

		return render(request, 'main/add-user.html', args)
	else:
		return redirect('/')


def registration(request):
	args = {}
	args.update(csrf(request))

	return render(request, 'main/registration.html', args)


def restore_password(request):
	if request.user.is_authenticated:
		args = get_username_and_status(request)
	else:
		args = {}

	return render(request, 'main/restore-password.html', args)


def load_pdf(request):
	if request.user.is_authenticated:
		args = get_username_and_status(request)

		return render(request, 'main/load-pdf-file.html', args)
	else:
		return redirect('/')