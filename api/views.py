from django.shortcuts import HttpResponse, redirect
from django.contrib.auth.models import User
from django.contrib import auth
from django.template.context_processors import csrf
from django.core.mail import send_mail
from django.core.files.storage import FileSystemStorage
from django.conf import settings

from main.models import Client


import httplib2, googleapiclient.discovery

from oauth2client.service_account import ServiceAccountCredentials


from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage

from xlutils.copy import copy as xlcopy

import json, secrets, string, time, os, io, re


try:
	creds_file_path = os.path.join(settings.BASE_DIR, 'api\creds.json')

	credentials = ServiceAccountCredentials.from_json_keyfile_name(
		creds_file_path,
		[
			'https://www.googleapis.com/auth/spreadsheets',
			'https://www.googleapis.com/auth/drive'
		]
	)
except:
	creds_file_path = os.path.join(settings.BASE_DIR, 'api/creds.json')

	credentials = ServiceAccountCredentials.from_json_keyfile_name(
		creds_file_path,
		[
			'https://www.googleapis.com/auth/spreadsheets',
			'https://www.googleapis.com/auth/drive'
		]
	)


httpAuth = credentials.authorize(httplib2.Http())
service = googleapiclient.discovery.build('sheets', 'v4', http = httpAuth)


media_base_dir = os.path.join(settings.BASE_DIR, 'media')


alphabet = string.ascii_letters + string.digits


def return_json_response(data, status_code = 200):
	response = HttpResponse(json.dumps(data), content_type = 'application/json')
	response.status_code = status_code
	return response


def login(request):
	if request.is_ajax() and request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']

		user = auth.authenticate(username = username, password = password)
		if user is not None:
			auth.login(request, user)
			result = {
				'status': 'accepted',
				'message': 'OK'
			}
		else:
			print(user)
			result = {
				'status': 'Not accepted',
				'message': 'Wrong username or password'
			}

		return return_json_response(result)
	else:
		result = {
			'status': 'Not accepted',
			'message': 'Wrong method'
		}
		return return_json_response(result, 400)


def logout(request):
	auth.logout(request)
	result = {
		'status': 'accepted',
		'message': 'Logout successful'
	}
	return redirect('/')


def add_user(request):
	if request.user.is_authenticated:
		if request.is_ajax() and request.method == 'POST':
			name = request.POST['name']
			surname = request.POST['surname']
			email = request.POST['email'].lower()
			status = request.POST['status']
			username = request.POST['username']
			password = request.POST['password']
			google_sheet_id = request.POST['google-sheet-id']

			client = Client.objects.get(account = request.user)
			if client.status != 'a':
				status = 'user'

			if len(User.objects.filter(username = username)) != 0:
				result = {
					'status': 'Not accepted',
					'message': 'Existing username'
				}
				return return_json_response(result)
			elif len(Client.objects.filter(email = email)) != 0:
				result = {
					'status': 'Not accepted',
					'message': 'Existing email'
				}
				return return_json_response(result)
			else:
				html_message = f'Congratulations, {name}!<br><br>\
								 Somebody (probably you) registered you in our\
								 <a href = "https://127.0.0.1:8000/" style = "color: blue; text-decoration: none;">small developing site</a><br><br>\
								 Your username: {username}<br>\
								 Your password: {password}<br><br>\
								 Enjoy!'
				send_mail('Account verification', 'Lol', 'Kek', [email], html_message = html_message)

				new_user = User.objects.create_user(username = username,
													password = password)
				if status == 'admin':
					new_user.is_staff = True
				new_user.save()

				if not request.user.is_authenticated:
					auth.login(request, new_user)

				new_client = Client(
					name = name,
					surname = surname,
					email = email,
					status = status[0],
					account = new_user,
					google_sheet_id = google_sheet_id
					)
				new_client.save()
				print('\n\nNew client was created\n\n')

				result = {
					'status': 'accepted',
					'message': 'OK'
				}
				return return_json_response(result, 201)
		else:
			result = {
				'status': 'Not accepted',
				'message': 'Wrong method'
			}
			return return_json_response(result, 400)
	else:
		result = {
			'status': 'Not accepted',
			'message': 'Authentication required'
		}
		return return_json_response(result, 401)


def restore_password(request):
	global alphabet

	if request.is_ajax() and request.method == 'POST':
		try:
			username = request.POST['username']
			if len(User.objects.filter(username = username)) == 0:
				result = {
					'status': 'Not accepted',
					'message': 'Usename does not exist'
				}
				return return_json_response(result)
			else:
				print(User.objects.filter(username = username))
				print(Client.objects.filter(account = User.objects.get(username = username)))
				client = Client.objects.get(account = User.objects.get(username = username))
				email = client.email
				success = True
		except:
			email = request.POST['email'].lower()
			if len(Client.objects.filter(email = email)) == 0:
				result = {
					'status': 'Not accepted',
					'message': 'Email does not exist'
				}
				return return_json_response(result)

		client = Client.objects.filter(email = email)[0]
		name = client.name
		user = client.account
		new_password = ''.join(secrets.choice(alphabet) for i in range(12))
		user.set_password(new_password)
		user.save()

		send_mail('Restoring password', '', '', [email], html_message = 'Hello, ' + name + '!<br><br>Your new password: ' + new_password + '<br><br>Enjoy!')
		result = {
			'status': 'accepted',
			'message': ''
		}
		return return_json_response(result)
	else:
		result = {
			'status': 'Not accepted',
			'message': 'Wrong method'
		}
		return return_json_response(result, 400)


def parse_pdf_file(request):
	def get_pdf_data(pdf_file_name):
		resource_manager = PDFResourceManager()
		fake_file_handle = io.StringIO()
		converter = TextConverter(resource_manager, fake_file_handle)
		page_interpreter = PDFPageInterpreter(resource_manager, converter)

		with open(pdf_file_name, 'rb') as fh:
			for page in PDFPage.get_pages(fh, 
										  caching=True,
										  check_extractable=True):
				page_interpreter.process_page(page)

			text = fake_file_handle.getvalue()

		converter.close()

		return text


	# function to get text between 2 substrings
	# gft is "Get Fixed Text"
	def gft(text, substr1, substr2, min_first_substr_index = 0, min_second_substr_index = 0):
		pos1 = text.lower().find(substr1.lower(), min_first_substr_index)
		if pos1 == -1:
			raise Exception('The first substring is not in the text')
		pos1 += len(substr1)

		pos2 = text.lower().find(substr2.lower(), max(pos1, min_second_substr_index))
		if pos2 == -1:
			pos2 = text.lower().find(substr2.lower())
			if pos2 == -1:
				raise Exception('The second substring is not in the text')
			elif pos2 < pos1:
				raise Exception(f'The second substirng occurs in the text earlier than the first one (pos1 = {pos1}, pos2 = {pos2})')

		return text[pos1 : pos2].strip()


	def get_data(filename, save_url):
		def extract_address(text):
			try:
				x = int(text[:6])
				return text[6:]
			except:
				return text[text.find(re.findall(r'[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?',\
							text)[0]):]


		text = get_pdf_data(filename)

		order_id = gft(text, 'Order ID:', 'Total Vehicles:')
		try:
			total_vehicles = gft(text, 'Total Vehicles:', 'Carrier Information')
		except:
			total_vehicles = gft(text, 'Total Vehicles:', 'CarrierInformation')
		try:
			carrier = gft(text, 'Carrier:', 'Driver:')
			driver = gft(text, 'Driver:', 'Driver Phone:')
			driver_phone = gft(text, 'Driver Phone:', 'Contact:')
		except:
			carrier = gft(text, 'Carrier:', 'Contact:')
			driver = ''
			driver_phone = ''
		contact = gft(text, 'Contact:', 'Phone:')
		min_phone_index = text.find('Contact:')
		try:
			contact_phones = [gft(text, 'Phone:', 'Phone 2:', min_phone_index)]
		except:
			contact_phones = [gft(text, 'Phone:', 'Order Information', min_phone_index)]
		try:
			contact_phones.append(gft(text, 'Phone 2:', 'Order Information'))
		except:
			pass
		dispatch_date = gft(text, 'Dispatch Date:', 'Pickup')
		pickup_exactly = gft(text, ':', 'Delivery', text.find('Pickup')).split('/')
		pickup_exactly = f'{pickup_exactly[1]}.{pickup_exactly[0]}.{pickup_exactly[2]}'
		delivery_estimated = gft(text, ':', 'Ship Via:', text.find('Delivery'))
		ship_via = gft(text, 'Ship Via:', 'Condition:')
		condition = gft(text, 'Condition:', 'Price')
		price = max([float(s) for s in re.findall(r'[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?',\
					 gft(text, ':', ' ', text.find('Price'), text.find(':', text.find('Company*')) + 2))])
		company_name = gft(text, 'Dispatch Sheet',\
						   re.findall(r'[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?',\
						   text[text.find('Dispatch Sheet'):])[0])
		if re.findall(r'[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?', text[text.find('Dispatch Sheet'):])[0][0] == '.':
			company_name += '.'
		company_data = gft(text, company_name, 'Co. Phone:')
		company_phone = gft(text, 'Co. Phone:', 'Dispatch InfoContact:')
		# di - Dispatch info
		di_contact = gft(text, 'Dispatch InfoContact:', 'Phone:')
		try:
			company_contact_phone = gft(text, 'Phone:', 'Fax:', text.find('Dispatch InfoContact:'))
			try:
				fax = gft(text, 'Fax:', 'MC #:', text.find('Dispatch InfoContact:'))
				try:
					company_mc = gft(text, 'MC #:', 'Vehicle Information')
				except:
					company_mc = ''
			except:
				fax = gft(text, 'Fax:', 'Vehicle Information', text.find('Dispatch InfoContact:'))
				company_mc = ''
		except:
			try:
				company_contact_phone = gft(text, 'Phone:', 'MC #:', text.find('Dispatch InfoContact:'))
			except:
				company_contact_phone = gft(text, 'Phone:', 'Vehicle Information', text.find('Dispatch InfoContact:'))
				company_mc = ''
			fax = ''
		vehicle_name = gft(text, '1', 'Type:', text.find('Vehicle Information'))
		vehicle_type = gft(text, 'Type:', 'Color:', text.find('Vehicle Information'))
		vehicle_color = gft(text, 'Color:', 'Plate:', text.find('Vehicle Information'))
		vehicle_plate = gft(text, 'Plate:', 'VIN:', text.find('Vehicle Information'))
		vehicle_vin = gft(text, 'VIN:', 'Lot #:', text.find('Vehicle Information'))
		try:
			vehicle_lot = gft(text, 'Lot #:', 'Additional Info:', text.find('Vehicle Information'))
			vehicle_additional_info = gft(text, 'Additional Info:', 'Pickup Information', text.find('Vehicle Information'))
		except:
			vehicle_lot = gft(text, 'Lot #:', 'AdditionalInfo:', text.find('Vehicle Information'))
			vehicle_additional_info = gft(text, 'AdditionalInfo:', 'Pickup Information', text.find('Vehicle Information'))
		# pi - Pickup information
		pi_address = extract_address(gft(text, 'Name:', 'Phone:', text.find('Pickup Information')).split(':')[-1])
		try:
			pi_phones = [gft(text, 'Phone:', 'Phone 2:', text.find('Pickup Information')),
						 gft(text, 'Phone 2:', 'Delivery Information', text.find('Pickup Information'))]
		except:
			pi_phones = [gft(text, 'Phone:', 'Delivery Information', text.find('Pickup Information'))]
		# di - Delivery information
		di_address = extract_address(gft(text, 'Name:', 'Phone:', text.find('Delivery Information')).split(':')[-1])
		try:
			di_phones = [gft(text, 'Phone:', 'Phone 2:', text.find('Delivery Information')),
						 gft(text, 'Phone 2:', 'DISPATCH INSTRUCTIONS', text.find('Delivery Information'))]
		except:
			di_phones = [gft(text, 'Phone:', 'DISPATCH INSTRUCTIONS', text.find('Delivery Information'))]
		emails = re.findall(r'[\w\.-]+@[\w\.-]+', text[text.find('DISPATCH INSTRUCTIONS'):])


		return [[company_name, order_id, company_phone, vehicle_name, str(price), '',\
				f"https://www.google.com/maps/search/?api=1&query={carrier.replace(' ', '+')}",
				', '.join(pi_phones), pickup_exactly,
				f"https://www.google.com/maps/search/?api=1&query={company_data.replace(' ', '+')}",
				', '.join(di_phones), '', save_url],
				['', '', '', '', '', '', '', '', '', '', delivery_estimated.replace('/', '.'),\
				 '', f'LOT #: {vehicle_lot}']]


	def write_to_googlesheet(data, sheet_id, start_row):
		global service

		to_write_values = [[
			'Broker',
			'Order ID',
			'Broker phone',
			'Vehicle',
			'Cost $',
			'Miles',
			'From Address',
			'Pickup Phone',
			'Pick Up Date',
			'To',
			'Receiver phone',
			'Deliver Date',
			'Disp Sheet',
			'BOL'
		]]
		values = service.spreadsheets().values().batchUpdate(
			spreadsheetId=sheet_id,
			body={
				'valueInputOption': 'USER_ENTERED',
				'data': [
					{
						'majorDimension': 'ROWS',
						'range': f'A1:X2',
						'values': to_write_values
					}
				]
			}
		).execute()

		print('Values written')

		values = service.spreadsheets().values().batchUpdate(
			spreadsheetId=sheet_id,
			body={
				'valueInputOption': 'USER_ENTERED',
				'data': [
					{
						'majorDimension': 'ROWS',
						'range': f'A{start_row}:X{start_row + 2}',
						'values': data
					}
				]
			}
		).execute()

		print('wsklfknjkdhfegnfejkrghnjtkr')


	if request.user.is_authenticated:
		client = Client.objects.get(account = request.user)
		filenames_to_parse = []
		for file in request.FILES.getlist('pdf-file'):
			filename = f"{client.account.username}/{time.time()}-{file.name}"
			filenames_to_parse.append(f'{media_base_dir}/{filename}')
			FileSystemStorage().save(filename, file)
		for filename in filenames_to_parse:
			write_to_googlesheet(
				get_data(filename, 'http://localhost:8000/media/' + '/'.join(filename.split('/')[-2:])),
				client.google_sheet_id,
				4 * client.number_of_parsed_files + 3
			)
			client.number_of_parsed_files += 1
		client.save()
		result = {
			'status': 'accepted',
			'message': 'Files parsed'
		}
		return return_json_response(result)
	else:
		result = {
			'status': 'Not accepted',
			'message': 'Authentication required'
		}
		return return_json_response(result, 401)