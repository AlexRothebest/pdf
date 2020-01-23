import io
 
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage

import re


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
# gft is Get Fixed Text
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


def get_info(filename):
	text = get_pdf_data(filename)
	print(text + '\n\n\n')

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
	pickup_exactly = gft(text, ':', 'Delivery', text.find('Pickup'))
	delivery_estimated = gft(text, ':', 'Ship Via:', text.find('Delivery'))
	ship_via = gft(text, 'Ship Via:', 'Condition:')
	condition = gft(text, 'Condition:', 'Price')
	# price_listed = gft(text, ':', 'Total Payment to Carrier:', text.find('Price'))
	# tp_to_carrier = gft(text, 'Total Payment to Carrier:', 'On')
	# od_to_carrier = gft(text, ':', 'Company', text.find('On', text.find('Total Payment to Carrier:')))
	# co_carrier = gft(text, ':', ' ', text.find('Company'))
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
	pi_name = gft(text, 'Name:', 'Phone:', text.find('Pickup Information'))
	try:
		pi_phones = [gft(text, 'Phone:', 'Phone 2:', text.find('Pickup Information')),
					 gft(text, 'Phone 2:', 'Delivery Information', text.find('Pickup Information'))]
	except:
		pi_phones = [gft(text, 'Phone:', 'Delivery Information', text.find('Pickup Information'))]
	# di - Delivery information
	di_name = gft(text, 'Name:', 'Phone:', text.find('Delivery Information'))
	try:
		di_phones = [gft(text, 'Phone:', 'Phone 2:', text.find('Delivery Information')),
					 gft(text, 'Phone 2:', 'DISPATCH INSTRUCTIONS', text.find('Delivery Information'))]
	except:
		di_phones = [gft(text, 'Phone:', 'DISPATCH INSTRUCTIONS', text.find('Delivery Information'))]
	emails = re.findall(r'[\w\.-]+@[\w\.-]+', text[text.find('DISPATCH INSTRUCTIONS'):])


	print('\n\n'.join([order_id, total_vehicles, carrier, driver, driver_phone, contact,\
		  ', '.join(contact_phones), dispatch_date, pickup_exactly, delivery_estimated,\
		  ship_via, condition, str(price), company_name, company_data, company_phone, di_contact,\
		  company_contact_phone, fax, company_mc, vehicle_name, vehicle_type, vehicle_color,\
		  vehicle_plate, vehicle_vin, vehicle_lot, vehicle_additional_info, pi_name,\
		  ', '.join(pi_phones), di_name, ', '.join(di_phones), ', '.join(emails)]))


for i in range(1, 19):
	get_info(f'proba{i}.pdf')
	print('\n\n' + '=' * 100 + '\n\n')