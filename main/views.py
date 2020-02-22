from django.shortcuts import render, redirect
from django.template.context_processors import csrf

from .models import Client


def get_username_and_status(request):
	client = Client.objects.get(account=request.user)

	args = {
		'client': client,
		'client_sheets': client.googlesheet_set.all()
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


def change_password(request):
	if request.user.is_authenticated:
		args = get_username_and_status(request)

		return render(request, 'main/change-password.html', args)
	else:
		return redirect('/')


def new_googlesheet(request):
	if request.user.is_authenticated:
		args = get_username_and_status(request)

		return render(request, 'main/new-googlesheet.html', args)
	else:
		return redirect('/')


def load_pdf(request):
	if request.user.is_authenticated:
		client = Client.objects.get(account=request.user)
		if len(client.googlesheet_set.all()) == 0:
			return redirect('/new-googlesheet/')

		args = get_username_and_status(request)

		return render(request, 'main/load-pdf-file.html', args)
	else:
		return redirect('/')