import csv

from .order import order

class importObj:
	pass

class csvObj(importObj):
	def __init__(self, filename : str):
		if filename is not None:
			self.filename = filename
			self.readOrders(filename)
	def readOrders(self, filename : str):
		with open(filename, newline='') as csvfile:
			orderList = csv.reader(csvfile, delimiter=',', quotechar='"')
			self.orders = []
			for orderRow in orderList:
				if orderRow[0] == 'Order':
					#if this is the description row, ignore it
					continue
				myOrder = order(orderRow)
				self.orders.append(myOrder)