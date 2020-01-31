from django.shortcuts import render, redirect
from django.template.context_processors import csrf

from .models import Client


def get_username_and_status(request):
	client = Client.objects.get(account=request.user)

	args = {
		'username': request.user.username,
		'status': client.status
	}

	return args


def home(request):
	return redirect('login/')


def login(request):
	if not request.user.is_authenticated:
		args = get_username_and_status(request)
		args.update(csrf(request))

		return render(request, 'main/login.html', args)
	else:
		return redirect('/load_pdf/')


def add_user(request):
	if request.user.is_authenticated:
		args = get_username_and_status(request)
		args.update(csrf(request))

		return render(request, 'main/add_user.html', args)
	else:
		return redirect('/')


def registration(request):
	if request.user.is_authenticated:
		args = get_username_and_status(request)
		args.update(csrf(request))

		return render(request, 'main/registration.html', args)
	else:
		return redirect('/')


def restore_password(request):
	args = get_username_and_status(request)

	return render(request, 'main/restore_password.html', args)


def load_pdf(request):
	if request.user.is_authenticated:
		client = Client.objects.get(account = request.user)
		status = client.status

		args = get_username_and_status(request)
		args.update(csrf(request))

		return render(request, 'main/load_pdf_file.html', args)
	else:
		return redirect('/')