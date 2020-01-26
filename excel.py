import xlwt, xlrd
from xlutils.copy import copy as xlcopy


def write_info(filename, data):
	if filename[-4:] != '.xls':
		if filename[-5:] != '.xlsx':
			filename += '.xls'
		else:
			filename = filename[:-5] + '.xls'

	file = xlcopy(xlrd.open_workbook(filename))
	sheet = file.get_sheet(0)

	row = len(sheet.rows) + 2

	for col, value in enumerate(data):
		sheet.write(row, col, value)

	file.save(filename)


write_info('Data', ['erjgeirg', 'ewpojgkeporg', 'eiwojhferjhghegori'])