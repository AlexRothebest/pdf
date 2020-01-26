import io, re, xlwt, xlrd
 
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage

from xlutils.copy import copy as xlcopy

from tkinter import *


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


def get_data(filename):
	def extract_address(text):
		try:
			x = int(text[:6])
			return text[6:]
		except:
			return text[text.find(re.findall(r'[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?',\
						text)[0]):]

	text = get_pdf_data(filename)
	# print(text + '\n\n\n')

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


	print('\n\n'.join([order_id, total_vehicles, carrier, driver, driver_phone, contact,\
		  ', '.join(contact_phones), dispatch_date, pickup_exactly, delivery_estimated,\
		  ship_via, condition, str(price), company_name, company_data, company_phone, di_contact,\
		  company_contact_phone, fax, company_mc, vehicle_name, vehicle_type, vehicle_color,\
		  vehicle_plate, vehicle_vin, vehicle_lot, vehicle_additional_info, pi_address,\
		  ', '.join(pi_phones), di_address, ', '.join(di_phones), ', '.join(emails)]))

	write_info('Data', [[company_name, order_id, company_phone, vehicle_name, str(price), '',\
				# xlwt.Formula(f'''HYPERLINK("https://www.google.com/maps/search/?api=1&query={carrier.replace(' ', '+')}"; "{carrier}")'''),
				pi_address,
				', '.join(pi_phones), pickup_exactly,
				# f'''=ГИПЕРССЫЛКА("https://www.google.com/maps/search/?api=1&query={company_data.replace(' ', '+')}";"{company_data}")''',
				di_address,
				', '.join(di_phones)],
				['', '', '', '', '', '', '', '', '', '', delivery_estimated.replace('/', '.'),\
				 '', f'LOT #: {vehicle_lot}']])

	return\
f'''Order ID: {order_id}

Carrier: {carrier}
Driver: {driver}
Driver phone: {driver_phone}

Contact: {contact}
Contact phones: {', '.join(contact_phones)}

Dispatch date: {dispatch_date}
Pickup exactly: {pickup_exactly}
Delivery estimated: {delivery_estimated}
Ship via: {ship_via}
Condition: {condition}

Price: {price}

Company name: {company_name}
Company data: {company_data}
Company phone: {company_phone}

Dispatch info contact: {di_contact}

Company contact phone: {company_contact_phone}
Fax: {fax}
MC: {company_mc}

Total vehicles: {total_vehicles}

Vehicle name: {vehicle_name}
Vehicle type: {vehicle_type}
Vehicle color: {vehicle_color}
Vehicle plate: {vehicle_plate}
Vehicle VIN: {vehicle_vin}
Vehicle lot: {vehicle_lot}
Vehicle additional info: {vehicle_additional_info}

Pickup information name: {pi_address}
Pickup information phones: {', '.join(pi_phones)}

Delivery information name: {di_address}
Delivery information phones: {', '.join(di_phones)}

Emails: {', '.join(emails)}
'''


def init_excel_file(data):
	filename = 'Data.xls'
	file = xlwt.Workbook()
	sheetname = 'Sheet'
	sheet = file.add_sheet(sheetname)

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
		'BOL'
	]
	for col, value in enumerate(to_write_values):
		sheet.write(0, col, value)

	file.save(filename)


def write_info(filename, data):
	if filename[-4:] != '.xls':
		if filename[-5:] != '.xlsx':
			filename += '.xls'
		else:
			filename = filename[:-5] + '.xls'

	workbook = xlrd.open_workbook(filename)
	file = xlcopy(workbook)
	sheet = file.get_sheet(0)

	row = len(sheet.rows) + 2

	for row_num, values in enumerate(data):
		for col, value in enumerate(values):
			sheet.write(row + row_num, col, value)

	file.save(filename)


def format_links(filename):
	if filename[-4:] != '.xls':
		if filename[-5:] != '.xlsx':
			filename += '.xls'
		else:
			filename = filename[:-5] + '.xls'

	workbook = xlrd.open_workbook(filename)
	read_sheet = workbook.sheet_by_index(0)
	file = xlcopy(workbook)
	sheet = file.get_sheet(0)

	linked_columns = [6, 9]
	for row in range(1, read_sheet.nrows):
		for col in linked_columns:
			value = read_sheet.cell_value(row, col)
			if value != '':
				sheet.write(row, col, xlwt.Formula(f'''HYPERLINK("https://www.google.com/maps/search/?api=1&query={value.replace(' ', '+')}"; "{value}")'''))

	file.save(filename)

# format_links('Data')
# exit()


def parse(event):
	global filename_field

	with open('Data.txt', 'w', encoding = 'UTF-8') as file:
		file.write(get_data(filename_field.get()))


# write_info('Data')
# exit()


root = Tk()
root.title('PDF parser')
root.minsize(420, 160)

Label(root, text = 'Имя PDF-файла:').place(x = 50, y = 30)

default_filename = StringVar()
default_filename.set('pdf files/proba7.pdf')
filename_field = Entry(root, textvariable = default_filename, width = 30)
filename_field.place(x = 190, y = 30)

start_button = Button(root, text = 'Спарсить', width = 20, height = 2)
start_button.bind('<Button-1>', parse)
start_button.place(x = 130, y = 80)

mainloop()

format_links('Data')