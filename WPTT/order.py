class order:
	def __init__(self, orderRow: list):
		self.orderRow		=	orderRow
		self.orderPlaced	=	orderRow[1]
		self.status			=	orderRow[10]
		self.currency		=	orderRow[2]
		self.subtotal		=	float(orderRow[3])
		self.shipping		=	float(orderRow[5])
		self.total			=	float(orderRow[6])
		self.refunded			=	orderRow[7]
		if self.refunded != "":
			self.refunded	=	float(self.refunded)

		self.custName		=	orderRow[14]
		self.custEmail		=	orderRow[15]
		self.custAddress	=	"{}\n{}\n{} {} {}".format(orderRow[17], orderRow[18], orderRow[20], orderRow[21], orderRow[19])
		self.custPhone		=	orderRow[16]

		self.deliveryInstructions = orderRow[13]
		
		self.isDelivery		=	(("DELIVER" in self.deliveryInstructions) or ("Delivery" in orderRow[9]))
		self.isPickup		=	not self.isDelivery
		self.pickupOrDeliver=	("Delivery" if self.isDelivery else "Pickup")
		

		self.productList	= []

		pickupDate			=	orderRow[8][:10]
		#convert US date to AU date
		self.pickupDate		=	pickupDate[3:6] + pickupDate[0:3] + pickupDate[6:10]
		self.product		=	orderRow[24]
		self.productQty		=	int(orderRow[23])
		self.productPrice	=	orderRow[29]
		self.productTotal	=	orderRow[30]

		self.productList.append((self.product, self.productQty, self.productPrice, self.productTotal))

		self.productStr = ", ".join(["{}x {}".format(x[1], x[0]) for x in self.productList])
	
	def __str__(self):
		nameStr = "{} : {} order for {}".format(self.pickupDate, self.pickupOrDeliver, self.custName)
		return "{} - {}".format(nameStr, self.productStr)
	
	def clone(self):
		return order(self.orderRow)