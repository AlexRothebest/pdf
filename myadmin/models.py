from django.db import models

from main.models import Client


class ParsedData(models.Model):
	company_name = models.CharField(max_length = 1000)
	order_id = models.CharField(max_length = 1000)
	company_phone = models.CharField(max_length = 1000)

	price = models.CharField(max_length = 1000)

	direction_length = models.IntegerField()
	direction_link = models.CharField(max_length = 1000)

	pi_address = models.CharField(max_length = 1000)
	di_address = models.CharField(max_length = 1000)
	origin_address_link = models.CharField(max_length = 1000)
	destination_address_link = models.CharField(max_length = 1000)

	pi_phone0 = models.CharField(max_length = 1000)
	pi_phone1 = models.CharField(max_length = 1000)
	di_phone0 = models.CharField(max_length = 1000)
	di_phone1 = models.CharField(max_length = 1000)

	pickup_exactly = models.CharField(max_length = 1000)
	delivery_estimated = models.CharField(max_length = 1000)

	emails = models.CharField(max_length = 1000)

	save_url = models.CharField(max_length = 1000)

	client = models.ForeignKey(Client, on_delete=models.CASCADE)


	def __str__(self):
		return self.order_id + ' --- ' + self.company_name


class Vehicle(models.Model):
	name = models.CharField(max_length = 1000)
	vehicle_type = models.CharField(max_length = 1000)
	color = models.CharField(max_length = 1000)
	plate = models.CharField(max_length = 1000)
	vin = models.CharField(max_length = 1000)
	lot = models.CharField(max_length = 1000)
	additional_info = models.CharField(max_length = 1000)

	file = models.ForeignKey(ParsedData, on_delete=models.CASCADE)


	def __str__(self):
		return self.file.order_id + ' - ' + self.file.company_name + ' : ' + self.name