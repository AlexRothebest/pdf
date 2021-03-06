from django.shortcuts import HttpResponse, redirect
from django.contrib.auth.models import User
from django.contrib import auth
from django.template.context_processors import csrf
from django.core.mail import send_mail
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.http import HttpResponse


from main.models import Client, GoogleSheet
from myadmin.models import ParsedData, Vehicle


import httplib2, googleapiclient.discovery, requests

from oauth2client.service_account import ServiceAccountCredentials


from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage

import tabula


from xlutils.copy import copy as xlcopy

import xlwt

from threading import Thread


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
	print('Looks like you are using not Windows\n')

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


with open(os.path.join(settings.BASE_DIR, 'api/google_api_keys.json'), 'r', encoding='UTF-8') as file:
	google_directions_api_key = json.loads(file.read())['directions_api_key']


media_base_dir = os.path.join(settings.BASE_DIR, 'media')


alphabet = string.ascii_letters + string.digits


def return_json_response(data, status_code = 200):
	response = HttpResponse(json.dumps(data), content_type = 'application/json')
	# response.status_code = status_code
	return response


def login(request):
	if request.is_ajax() and request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']

		user = auth.authenticate(username = username, password = password)
		if user is not None:
			auth.login(request, user)
			result = {
				'status': 'Accepted',
				'message': 'OK'
			}
		else:
			try:
				username = Client.objects.get(email=username).account.username

				user = auth.authenticate(username = username, password = password)
				if user is not None:
					auth.login(request, user)
					result = {
						'status': 'Accepted',
						'message': 'OK'
					}
			except:
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
		'status': 'Accepted',
		'message': 'Logout successful'
	}
	return redirect('/')


def add_user(request):
	if request.is_ajax() and request.method == 'POST':
		name = request.POST['name']
		email = request.POST['email'].lower()
		status = request.POST['status']
		username = request.POST['username']
		password = request.POST['password']

		if request.user.is_authenticated:
			client = Client.objects.get(account = request.user)
			if client.status != 'a':
				status = 'user'
		else:
			status = 'user'

		if len(User.objects.filter(username = username)) != 0:
			result = {
				'status': 'Not accepted',
				'message': 'This username is already taken'
			}
			return return_json_response(result)
		elif len(Client.objects.filter(email = email)) != 0:
			result = {
				'status': 'Not accepted',
				'message': 'This email is already taken'
			}
			return return_json_response(result)
		else:
			html_message = f'Congratulations, {name}!<br><br>\
							 Somebody (probably you) registered you in our\
							 <a href = "http://pdf.truckdispatch.pro" style = "color: blue; text-decoration: none;">site</a><br><br>\
							 Your username: {username}<br>\
							 Your password: {password}<br><br>\
							 Please send us your user experience to this email admin@truckdispatch.pro most reasonable things will be implemented ASAP'

			send_mail(
				'Scan PDF Account Registration',
				'', '',
				[email], 
				html_message = html_message
			)


			new_user = User.objects.create_user(username=username,
												password=password)
			if status == 'admin':
				new_user.is_staff = True
				new_user.is_superuser = True
			new_user.save()

			if not request.user.is_authenticated:
				auth.login(request, new_user)

			new_client = Client(
				name = name,
				email = email,
				status = status[0],
				account = new_user,
			)
			new_client.save()
			print('\n\nNew client was created\n\n')

			result = {
				'status': 'Accepted',
				'message': 'OK'
			}
			return return_json_response(result, 201)
	else:
		result = {
			'status': 'Not accepted',
			'message': 'Wrong method'
		}
		return return_json_response(result, 400)


def restore_password(request):
	global alphabet

	if request.is_ajax() and request.method == 'POST':
		try:
			username = request.POST['username'].lower()

			print(f'Restoring password by username {username}')

			if len(User.objects.filter(username = username)) == 0:
				result = {
					'status': 'Not accepted',
					'message': 'Usename does not exist'
				}
				return return_json_response(result)
			else:
				# print(User.objects.filter(username = username))
				# print(Client.objects.filter(account = User.objects.get(username = username)))
				client = Client.objects.get(account = User.objects.get(username = username))
				email = client.email
				success = True
		except:
			email = request.POST['email'].lower()

			print(f'Restoring password by email {email}')

			if len(Client.objects.filter(email = email)) == 0:
				result = {
					'status': 'Not accepted',
					'message': 'Email does not exist'
				}
				return return_json_response(result)

		client = Client.objects.filter(email = email)[0]
		name = client.name
		user = client.account
		if user.username == 'admin':
			new_password = 'admin'
		else:
			new_password = ''.join(secrets.choice(alphabet) for i in range(12))
		user.set_password(new_password)
		user.save()

		send_mail(
			'Truckdispatch.pro Reset password',
			'', '',
			[email],
			html_message = f'''Hello, {name}!<br><br>
							   Your new password: {new_password}<br><br>
							   Stay with us!'''
		)

		result = {
			'status': 'Accepted',
			'message': ''
		}
		return return_json_response(result)
	else:
		result = {
			'status': 'Not accepted',
			'message': 'Wrong method'
		}
		return return_json_response(result, 400)


def change_password(request):
	if request.user.is_authenticated:
		if request.is_ajax() and request.method == 'POST':
			client = Client.objects.get(account = request.user)

			old_password = request.POST['oldPassword']
			new_password = request.POST['newPassword']

			user = client.account
			if user.check_password(old_password):
				user.set_password(new_password)
				user.save()

				result = {
					'status': 'Accepted',
					'message': ''
				}
				return return_json_response(result)
			else:
				result = {
					'status': 'Not accepted',
					'message': 'Wrong password'
				}
				return return_json_response(result, 200)
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
		return return_json_response(result, 400)


def change_clients_data(request):
	if request.user.is_authenticated:
		if request.is_ajax() and request.method == 'POST':
			client = Client.objects.get(account = request.user)
			if client.status != 'a':
				result = {
					'status': 'Not accepted',
					'message': 'Permission denied'
				}
				return return_json_response(result, 403)

			for client_id, new_status in request.POST.items():
				client_to_change = Client.objects.get(id=int(client_id))
				client_to_change.status = new_status[0]
				client_to_change.save()

				user = client_to_change.account
				user.is_staff = new_status=='admin'
				user.is_superuser = new_status=='admin'
				user.save()

			result = {
				'status': 'Accepted',
				'message': ''
			}
			return return_json_response(result)
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
		return return_json_response(result, 400)


def delete_clients(request):
	if request.user.is_authenticated:
		if request.is_ajax() and request.method == 'POST':
			client = Client.objects.get(account = request.user)
			if client.status != 'a':
				result = {
					'status': 'Not accepted',
					'message': 'Permission denied'
				}
				return return_json_response(result, 403)

			clients_to_delete = request.POST['clientsToDelete'].split(', ')
			deleted_clients_number, not_deleted_clients_number = 0, 0
			for client_id in clients_to_delete:
				try:
					Client.objects.get(id=int(client_id)).account.delete()
					deleted_clients_number += 1
				except:
					not_deleted_clients_number += 1

			result = {
				'status': 'Accepted',
				'message': f"{deleted_clients_number} clients deleted successfully, {not_deleted_clients_number} clients weren't deleted"
			}
			return return_json_response(result)
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
		return return_json_response(result, 400)


def add_new_googlesheet(request):
	def init_googlesheet(sheet_id):
		global service

		to_write_values = [[
			'Broker',
			'Order ID',
			'Broker phone',
			'Vehicle',
			'Cost $',
			'Miles',
			'Price per mile',
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
						'range': 'A1:X2',
						'values': to_write_values
					}
				]
			}
		).execute()


	if request.user.is_authenticated:
		if request.is_ajax() and request.method == 'POST':
			client = Client.objects.get(account = request.user)


			google_sheet_name = request.POST['nameOfTheGoogleSheet']
			google_sheet_id = request.POST['linkToTheGoogleSheet']


			if len(client.googlesheet_set.filter(name=google_sheet_name)) != 0:
				result = {
					'status': 'Not accepted',
					'message': 'Existing name'
				}
				return return_json_response(result)
			elif len(client.googlesheet_set.filter(sheet_id=google_sheet_id)) != 0:
				result = {
					'status': 'Not accepted',
					'message': 'Existing link'
				}
				return return_json_response(result)


			try:
				init_googlesheet(google_sheet_id)
			except:
				result = {
					'status': 'Not accepted',
					'message': 'Not prepared googlesheet'
				}
				return return_json_response(result)


			GoogleSheet(
				name=google_sheet_name,
				sheet_id=google_sheet_id,

				owner=client
			).save()


			result = {
				'status': 'Accepted',
				'message': ''
			}
			return return_json_response(result)
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
		return return_json_response(result, 400)


def parse_pdf_file(request):
	class PDFVehicle():
		pass


	def create_thread(function, args = ()):
		while True:
			try:
				Thread(target = function, args = args).start()
				print('Thread created')
				break
			except:
				time.sleep(3)


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
				# print(f'\n\n\nText: {text[pos1:]}\n\n\nSubstr 1: {substr1}\n\n\nSubstr 2: {substr2}\n\n\n')
				raise Exception(f'The second substring is not in the text')
			elif pos2 < pos1:
				# print(f'\n\n\nText: {text[pos1:]}\n\n\nSubstr 1: {substr1}\n\n\nSubstr 2: {substr2}\n\n\n')
				raise Exception(f'The second substring occurs in the text earlier than the first one (pos1 = {pos1}, pos2 = {pos2})')

		return text[pos1 : pos2].strip()


	def get_data(filename, save_url, client):
		def extract_address(text):
			if '*CONTACT DISPATCHER*' in text:
				return text.split('*CONTACT DISPATCHER*')[-1]

			try:
				x = int(text[:6])
				address = text[6:]
			except:
				address = text[text.find(re.findall(r'[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?',\
							   text)[0]):]

			for i in range(len(address)):
				for j in range(7, min(30, (len(address) - i) // 2)):
					# print(address[i : i + j])
					# print(address[i + j : i + 2 * j])
					if address[i : i + j] == address[i + j : i + 2 * j]:
						return address[i + j:]

			return address

		# print('\n\n')
		# print(extract_address('6-75 Truck & Auto Repair)32800 Dequindre Rd32800 Dequindre Rdwarren, MI 48092'))
		# print('\n\n')


		text = get_pdf_data(filename)
		# print(text)

		order_id = gft(text, 'Order ID:', 'Total Vehicles:')
		try:
			print(f'Parsed: {order_id}')
		except:
			pass
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
		price = max([float(s.replace(',', '')) for s in re.findall(r'[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?',\
					 gft(text, ':', ' ', text.find('Price'), text.find(':', text.find('Company*')) + 2))])
		company_name = gft(text, 'Dispatch Sheet',\
						   [number for number in\
						   re.findall(r'[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?',\
						   text[text.find('Dispatch Sheet'):])\
						   if len(number) >= 2][0])
		print(company_name)
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
		vehicles = []
		start_position = text.find('Vehicle Information')
		for vehicle_number in range(1, 100):
			# print(vehicle_number)
			vehicle = PDFVehicle()
			vehicle.name = gft(text, str(vehicle_number), 'Type:', start_position)
			vehicle.type = gft(text, 'Type:', 'Color:', start_position)
			vehicle.color = gft(text, 'Color:', 'Plate:', start_position)
			vehicle.plate = gft(text, 'Plate:', 'VIN:', start_position)
			vehicle.vin = gft(text, 'VIN:', 'Lot #:', start_position)
			try:
				try:
					vehicle.lot = gft(text, 'Lot #:', 'Additional Info:', start_position)
					vehicle.additional_info = gft(text, 'Additional Info:', 'Pickup Information', start_position)
				except:
					vehicle.lot = gft(text, 'Lot #:', 'AdditionalInfo:', start_position)
					vehicle.additional_info = gft(text, 'AdditionalInfo:', 'Pickup Information', start_position)
				if 'Additional Info:' in vehicle.additional_info or 'AdditionalInfo:' in vehicle.additional_info:
					a = 1 / 0
				vehicles.append(vehicle)
				break
			except:
				try:
					vehicle.additional_info = gft(text, 'Additional Info:', f'{vehicle_number + 1}  ', start_position)
					start_position = text.find(f'{vehicle_number + 1}  ', text.find('Additional Info:', start_position))
				except:
					vehicle.additional_info = gft(text, 'AdditionalInfo:', f'{vehicle_number + 1}  ', start_position)
					start_position = text.find(f'{vehicle_number + 1}  ', text.find('AdditionalInfo:', start_position))

				vehicles.append(vehicle)


		# pi - Pickup information
		pi_address = extract_address(gft(text, 'Name:', 'Phone:', text.find('Pickup Information')).split(':')[-1])
		# pi_phones = re.findall(r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})',\
		# 					   gft(text, 'Phone:', 'Delivery Information', text.find('Pickup Information')))
		try:
			try:
				try:
					pi_phones = [gft(text, 'Phone:', 'Phone 2:', text.find('Pickup Information')),
								 gft(text, 'Phone 2:', 'Phone 3:', text.find('Pickup Information')),
								 gft(text, 'Phone 3:', 'Cell:', text.find('Pickup Information'))]
				except:
					pi_phones = [gft(text, 'Phone:', 'Phone 2:', text.find('Pickup Information')),
								 gft(text, 'Phone 2:', 'Phone 3:', text.find('Pickup Information')),
								 gft(text, 'Phone 3:', 'Delivery Information', text.find('Pickup Information'))]
			except:
				pi_phones = [gft(text, 'Phone:', 'Phone 2:', text.find('Delivery Information')),
							 gft(text, 'Phone 2:', 'Delivery Information', text.find('Pickup Information'))]
		except:
			pi_phones = [gft(text, 'Phone:', 'Delivery Information', text.find('Pickup Information')), '']

		# di - Delivery information
		di_address = extract_address(gft(text, 'Name:', 'Phone:', text.find('Delivery Information')).split(':')[-1])
		try:
			try:
				try:
					di_phones = [gft(text, 'Phone:', 'Phone 2:', text.find('Delivery Information')),
								 gft(text, 'Phone 2:', 'Phone 3:', text.find('Delivery Information')),
								 gft(text, 'Phone 3:', 'Cell:', text.find('Delivery Information'))]
				except:
					di_phones = [gft(text, 'Phone:', 'Phone 2:', text.find('Delivery Information')),
								 gft(text, 'Phone 2:', 'Phone 3:', text.find('Delivery Information')),
								 gft(text, 'Phone 3:', 'DISPATCH INSTRUCTIONS', text.find('Delivery Information'))]
			except:
				di_phones = [gft(text, 'Phone:', 'Phone 2:', text.find('Delivery Information')),
							 gft(text, 'Phone 2:', 'DISPATCH INSTRUCTIONS', text.find('Delivery Information'))]
		except:
			di_phones = [gft(text, 'Phone:', 'DISPATCH INSTRUCTIONS', text.find('Delivery Information')), '']
		emails = re.findall(r'[\w\.-]+@[\w\.-]+', text[text.find('DISPATCH INSTRUCTIONS'):])


		direction_api_url = f'https://maps.googleapis.com/maps/api/directions/json?origin={pi_address}&destination={di_address}&mode=driving&traffic_model=pessimistic&departure_time=now&key={google_directions_api_key}'.replace('#', '%23')
		data = json.loads(requests.get(direction_api_url).text)
		direction_length = int(data['routes'][0]['legs'][0]['distance']['text'].replace(',', '').split('mi')[0].strip())
		origin_place_id = data['geocoded_waypoints'][0]['place_id']
		destination_place_id = data['geocoded_waypoints'][1]['place_id']
		direction_link = f'https://www.google.com/maps/dir/?api=1&origin={pi_address}&origin_place_id={origin_place_id}&destination={di_address}&destination_place_id={destination_place_id}&travelmode=driving'.replace(' ', '+')
		origin_address_link = f'https://www.google.com/maps/search/?api=1&query={pi_address}&query_place_id={origin_place_id}'.replace(' ', '+')
		destination_address_link = f'https://www.google.com/maps/search/?api=1&query={di_address}&query_place_id={destination_place_id}'.replace(' ', '+')

		parsed_data = ParsedData(
			company_name=company_name,
			order_id=order_id,
			company_phone=company_phone,

			price=price,

			direction_length=direction_length,
			direction_link=direction_link,

			pi_address=pi_address,
			di_address=di_address,
			origin_address_link=origin_address_link,
			destination_address_link=destination_address_link,

			pi_phone0=pi_phones[0],
			pi_phone1=pi_phones[1],
			di_phone0=di_phones[0],
			di_phone1=di_phones[1],

			pickup_exactly=pickup_exactly,
			delivery_estimated=delivery_estimated,

			emails=', '.join(emails),

			save_url=save_url,

			client=client
		)
		parsed_data.save()

		for vehicle in vehicles:
			Vehicle(
				name=vehicle.name,
				lot=vehicle.lot,

				file=parsed_data
			).save()

		vehicle = vehicles[0]
		data_to_return = [[company_name, order_id, company_phone, '', price,
						   f'=ГИПЕРССЫЛКА("{direction_link}";"{direction_length}")',
						   round(price/direction_length, 2),
						   f'=ГИПЕРССЫЛКА("{origin_address_link}";"{pi_address}")',
						   '', pickup_exactly,
						   f'=ГИПЕРССЫЛКА("{destination_address_link}";"{di_address}")',
						   '', delivery_estimated.replace('/', '.'), save_url.replace(' ', '%20')],
						   ['', '', '', '', '', '', '', '', '', '', '',\
						    '', '', '   '.join(f'LOT #: {vehicle.lot}' for vehicle in vehicles)]]
		for vehicle_number in range(len(vehicles)):
			try:
				data_to_return[vehicle_number][3] = vehicles[vehicle_number].name
			except:
				data_to_return.append(['', '', '', vehicles[vehicle_number].name,
									   '', '', '', '', '', '', '', '', ''])

		for pi_phone_number in range(len(pi_phones)):
			try:
				data_to_return[pi_phone_number][8] = pi_phones[pi_phone_number]
			except:
				data_to_return.append(['', '', '', '', '', '', '', '',
									   pi_phones[pi_phone_number],  '', '', ''])

		for di_phone_number in range(len(di_phones)):
			try:
				data_to_return[di_phone_number][11] = di_phones[di_phone_number]
			except:
				data_to_return.append(['', '', '',  '', '', '', '', '', '', '', '',
									   di_phones[di_phone_number], ''])

		return data_to_return


	def get_data2(filename, save_url, client):
		class PDFVehicle():
			pass


		def extract_address(text):
			if '*CONTACT DISPATCHER*' in text:
				return text.split('*CONTACT DISPATCHER*')[-1].strip()

			try:
				x = int(text[:6])
				address = text[6:]
			except:
				address = text[text.find(re.findall(r'[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?',\
							   text)[0]):]

			for i in range(len(address)):
				for j in range(7, min(30, (len(address) - i) // 2)):
					# print(address[i : i + j])
					# print(address[i + j : i + 2 * j])
					if address[i : i + j] == address[i + j : i + 2 * j]:
						return address[i + j:]

			return address.strip()


		text = get_pdf_data(filename)
		text = text[text.find('Order #'):]
		# print(text)

		order_id = gft(text, 'Order #:', 'Equipment')
		price = float(gft(text, 'Rate:', 'Carrier').replace('$', ''))
		company_name = gft(text, 'Carrier:', 'Phone')
		company_phone = gft(text, 'Phone #:', 'Dispatcher')
		pi_address = ' '.join([gft(text, 'Address:', 'City'), gft(text, 'City:', 'State'),\
							   gft(text, 'State:', 'Zip:'), gft(text, 'Zip:', 'Contact')])
		pi_phones = re.findall(r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})',\
							   gft(text, 'Phone #:', 'Pick', text.find('Address')))
		pickup_exactly = gft(text, 'Pick Up date and/or window:', 'Pick Up').split('/')
		pickup_exactly = f'{pickup_exactly[1]}.{pickup_exactly[0]}.{pickup_exactly[2]}'


		data = tabula.read_pdf(filename, pages='all')[0].iloc
		vehicles = []
		for vehicle_number in range(100):
			try:
				vehicle = PDFVehicle()
				vehicle.name = f'{data[vehicle_number, 0]} {data[vehicle_number, 1]} {data[vehicle_number, 2]}'
				vehicle.lot = data[vehicle_number, 5]
				vehicles.append(vehicle)
			except:
				break


		text = text[text.find(data[0, 3]):]


		di_address = ' '.join([gft(text, 'Address:', 'City'), gft(text, 'City:', 'State'),\
							   gft(text, 'State:', 'Zip:'), gft(text, 'Zip:', 'Contact')])
		di_phones = re.findall(r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})',\
							   gft(text, 'Phone #:', 'Delivery', text.find('Address')))
		delivery_estimated = gft(text, 'Delivery date and/or window:', 'Delivery').split('/')
		delivery_estimated = f'{delivery_estimated[1]}.{delivery_estimated[0]}.{delivery_estimated[2]}'

		emails = re.findall(r'[\w\.-]+@[\w\.-]+', text)


		direction_api_url = f'https://maps.googleapis.com/maps/api/directions/json?origin={pi_address}&destination={di_address}&mode=driving&traffic_model=pessimistic&departure_time=now&key={google_directions_api_key}'.replace('#', '%23')
		data = json.loads(requests.get(direction_api_url).text)
		direction_length = int(data['routes'][0]['legs'][0]['distance']['text'].replace(',', '').split('mi')[0].strip())
		origin_place_id = data['geocoded_waypoints'][0]['place_id']
		destination_place_id = data['geocoded_waypoints'][1]['place_id']
		direction_link = f'https://www.google.com/maps/dir/?api=1&origin={pi_address}&origin_place_id={origin_place_id}&destination={di_address}&destination_place_id={destination_place_id}&travelmode=driving'.replace(' ', '+')
		origin_address_link = f'https://www.google.com/maps/search/?api=1&query={pi_address}&query_place_id={origin_place_id}'.replace(' ', '+')
		destination_address_link = f'https://www.google.com/maps/search/?api=1&query={di_address}&query_place_id={destination_place_id}'.replace(' ', '+')


		data_to_return = [[company_name, order_id, company_phone, '', price,
						   f'=ГИПЕРССЫЛКА("{direction_link}";"{direction_length}")',
						   round(price/direction_length, 2),
						   f'=ГИПЕРССЫЛКА("{origin_address_link}";"{pi_address}")',
						   '', pickup_exactly,
						   f'=ГИПЕРССЫЛКА("{destination_address_link}";"{di_address}")',
						   '', delivery_estimated.replace('/', '.'), save_url.replace(' ', '%20')],
						   ['', '', '', '', '', '', '', '', '', '', '',\
						    '', '', '   '.join(f'LOT #: {vehicle.lot}' for vehicle in vehicles)]]

		parsed_data = ParsedData(
			company_name=company_name,
			order_id=order_id,
			company_phone=company_phone,

			price=price,

			direction_length=direction_length,
			direction_link=direction_link,

			pi_address=pi_address,
			di_address=di_address,
			origin_address_link=origin_address_link,
			destination_address_link=destination_address_link,

			pi_phone0=pi_phones[0],
			pi_phone1=pi_phones[1],
			di_phone0=di_phones[0],
			di_phone1=di_phones[1],

			pickup_exactly=pickup_exactly,
			delivery_estimated=delivery_estimated,

			emails=', '.join(emails),

			save_url=save_url,

			client=client
		)
		parsed_data.save()

		for vehicle in vehicles:
			Vehicle(
				name=vehicle.name,
				lot=vehicle.lot,

				file=parsed_data
			).save()

		for vehicle_number in range(len(vehicles)):
			try:
				data_to_return[vehicle_number][3] = vehicles[vehicle_number].name
			except:
				data_to_return.append(['', '', '', vehicles[vehicle_number].name,
									   '', '', '', '', '', '', '', '', ''])

		for pi_phone_number in range(len(pi_phones)):
			try:
				data_to_return[pi_phone_number][8] = pi_phones[pi_phone_number]
			except:
				data_to_return.append(['', '', '', '', '', '', '', '',
									   pi_phones[pi_phone_number],  '', '', ''])

		for di_phone_number in range(len(di_phones)):
			try:
				data_to_return[di_phone_number][11] = di_phones[di_phone_number]
			except:
				data_to_return.append(['', '', '',  '', '', '', '', '', '', '', '',
									   di_phones[di_phone_number], ''])

		return data_to_return



	def write_to_googlesheet(data, sheet_id, start_row):
		global service

		values = service.spreadsheets().values().batchUpdate(
			spreadsheetId=sheet_id,
			body={
				'valueInputOption': 'USER_ENTERED',
				'data': [
					{
						'majorDimension': 'ROWS',
						'range': f'A{start_row}:X{start_row + len(data)}',
						'values': data
					}
				]
			}
		).execute()


	if request.user.is_authenticated:
		if request.method == 'POST':
			media_base_url = f"http://{request.build_absolute_uri().split('://')[1].split('/')[0]}/media"

			client = Client.objects.get(account = request.user)

			google_sheet_id = request.headers['googleSheetId']
			try:
				google_sheet = client.googlesheet_set.get(sheet_id=google_sheet_id)
			except:
				result = {
					'status': 'Not accepted',
					'message': 'Wrong googlesheet id'
				}
				return return_json_response(result, 401)
			google_sheet.next_row_to_write_data = int(request.headers['nextRowToWriteData'])

			filenames_to_parse = []
			for file in request.FILES.getlist('pdf-file'):
				time_now = time.time()
				file_name = file.name
				file_path = f'{media_base_dir}/{client.account.username}/{time_now}-{file_name}'
				file_url = f'{media_base_url}/{client.account.username}/{time_now}-{file_name}'

				filenames_to_parse.append([file_name, file_path, file_url])

				FileSystemStorage().save(file_path, file)

			error_filenames = {}
			parsed_filenames = {}
			for file_name, file_path, file_url in filenames_to_parse:
				try:
					try:
						data = get_data(file_path, file_url, client)
					except:
						data = get_data2(file_path, file_url, client)
					write_to_googlesheet(
						data,
						google_sheet_id,
						google_sheet.next_row_to_write_data
					)

					client.number_of_parsed_files += 1
					google_sheet.next_row_to_write_data += len(data) + 2

					parsed_filenames[file_name] = file_url
				except Exception as error:
					print(f"\n\nFile {file_path} can't be parsed\nError: {repr(error)}\n\n")

					error_filenames[file_name] = file_url

			client.save()
			google_sheet.save()

			result = {
				'status': 'Accepted',
				'message': f'{len(filenames_to_parse) - len(error_filenames)} file(s) were scaned successfully',
				'google_sheet_id': google_sheet_id,
				'parsed_filenames': parsed_filenames,
				'error_filenames': error_filenames,
				'next_row_to_write_data': google_sheet.next_row_to_write_data
			}
			if len(error_filenames) > 0:
				result['message'] += f", {len(error_filenames)} file(s) can't be scaned"
			return return_json_response(result)
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


def download_clients_parsed_data(request):
	if request.user.is_authenticated:
		if request.is_ajax() and request.method == 'POST':
			client = Client.objects.get(account = request.user)
			if client.status != 'a':
				result = {
					'status': 'Not accepted',
					'message': 'Permission denied'
				}
				return return_json_response(result, 403)

			clients_to_download = request.POST['clientsToDownload'].split(', ')
			parsed_files_to_download = []
			for client_id in clients_to_download:
				parsed_files_to_download += Client.objects.get(id=int(client_id)).parseddata_set.all()
				# try:
				# 	parsed_files_to_download += Client.objects.get(id=int(client_id)).parseddata_set()
				# except:
				# 	pass

			print(f'Data from {len(parsed_files_to_download)} files will be downloaded now')

			response = HttpResponse(content_type='application/ms-excel')
			response['Content-Disposition'] = 'attachment; filename="Data.xls"'

			wb = xlwt.Workbook()
			ws = wb.add_sheet('Sheet 1')

			to_write_values = [
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
				'BOL',
				'Emails'
			]
			for col, value in enumerate(to_write_values):
				ws.write(0, col, value)

			for parsed_file_number, parsed_file in enumerate(parsed_files_to_download):
				row = 4 * parsed_file_number + 2

				ws.write(row, 0, parsed_file.company_name)
				ws.write(row, 1, parsed_file.order_id)
				ws.write(row, 2, parsed_file.company_phone)
				ws.write(row, 3, parsed_file.vehicle_set.all()[0].name)
				ws.write(row, 4, parsed_file.price)

				if len(parsed_file.direction_link) <= 255:
					ws.write(row, 5, xlwt.Formula(f'HYPERLINK("{parsed_file.direction_link}"; "{parsed_file.direction_length}")'))
				else:
					ws.write(row, 5, parsed_file.direction_link)
					ws.write(row + 1, 5, parsed_file.direction_length)

				if len(parsed_file.origin_address_link) <= 255:
					ws.write(row, 6, xlwt.Formula(f'HYPERLINK("{parsed_file.origin_address_link}"; "{parsed_file.pi_address}")'))
				else:
					ws.write(row, 6, parsed_file.origin_address_link)
					ws.write(row + 1, 6, parsed_file.pi_address)

				ws.write(row, 7, parsed_file.pi_phone0)
				ws.write(row, 8, parsed_file.pickup_exactly)

				if len(parsed_file.destination_address_link) <= 255:
					ws.write(row, 9, xlwt.Formula(f'HYPERLINK("{parsed_file.destination_address_link}"; "{parsed_file.di_address}")'))
				else:
					ws.write(row, 9, parsed_file.destination_address_link)
					ws.write(row + 1, 9, parsed_file.di_address)

				ws.write(row, 10, parsed_file.di_phone0)
				ws.write(row, 11, parsed_file.delivery_estimated.replace('/', '.'))
				ws.write(row, 12, xlwt.Formula(f'HYPERLINK("{parsed_file.save_url}"; "{parsed_file.save_url}")'))
				ws.write(row, 13, parsed_file.emails)

				ws.write(row + 1, 7, parsed_file.pi_phone1)
				ws.write(row + 1, 10, parsed_file.di_phone1)
				ws.write(row + 1, 12, f'LOT #: {parsed_file.vehicle_set.all()[0].lot}')


			for col in range(14):
				ws.col(col).width = 256 * 15

			wb.save(response)

			return response
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
		return return_json_response(result, 400)