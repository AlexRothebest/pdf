from django.shortcuts import render, redirect
from django.template.context_processors import csrf

from .models import Client


def home(request):
	return redirect('login/')


def login(request):
	if not request.user.is_authenticated:
		args = {}
		args.update(csrf(request))

		return render(request, 'main/login.html', args)
	else:
		return redirect('/load_pdf/')


def add_user(request):
	if request.user.is_authenticated:
		client = Client.objects.get(account = request.user)
		status = client.status

		args = {}
		args.update(csrf(request))
		args['admin'] = client.status == 'a'
		args['status'] = status
		return render(request, 'main/add_user.html', args)
	else:
		return redirect('/')


def registration(request):
	args = {}
	return render(request, 'main/registration.html', args)


def restore_password(request):
	args = {}
	return render(request, 'main/restore_password.html', args)


def load_pdf(request):
	if request.user.is_authenticated:
		client = Client.objects.get(account = request.user)
		status = client.status

		args = {}
		args.update(csrf(request))
		args['admin'] = client.status == 'a'
		args['status'] = status
		return render(request, 'main/load_pdf_file.html', args)
	else:
		return redirect('/')