class order:
	def __init__(self, orderRow: list):
		self.orderRow		=	orderRow
		self.orderPlaced	=	orderRow[2]
		self.status			=	orderRow[11]
		self.currency		=	orderRow[3]
		self.subtotal		=	float(orderRow[4])
		# Shipping can be 0 or blank. blank is interpreted as an empty string, which float(x) doesn't like
		self.shipping		=	orderRow[5]
		if (self.shipping != ""):
			self.shipping		=	float(self.shipping)
		self.total			=	float(orderRow[7])
		# refunded can be 0 or blank. blank is interpreted as an empty string, which float(x) doesn't like
		self.refunded			=	orderRow[8]
		if self.refunded != "":
			self.refunded	=	float(self.refunded)

		self.custName		=	orderRow[15]
		self.custEmail		=	orderRow[16]
		self.custAddress	=	"{}\n{}\n{} {} {}".format(
			orderRow[18],
			orderRow[19],
			orderRow[21],
			orderRow[22],
			orderRow[20])
		self.custPhone		=	orderRow[17]

		self.deliveryInstructions = orderRow[14]
		
		self.isDelivery		=	(("DELIVER" in self.deliveryInstructions) or ("Delivery" in orderRow[10]))
		self.isPickup		=	not self.isDelivery
		self.pickupOrDeliver=	("Delivery" if self.isDelivery else "Pickup")
		

		self.productList	= []

		self.pickupDate			=	orderRow[9][:10]
		self.product		=	orderRow[25]
		self.productQty		=	int(orderRow[24])
		self.productPrice	=	orderRow[29]
		self.productTotal	=	orderRow[30]

		self.productList.append((self.product, self.productQty, self.productPrice, self.productTotal))

		self.productStr = ", ".join(["{}x {}".format(x[1], x[0]) for x in self.productList])
	
	def __str__(self):
		nameStr = "{} : {} order for {}".format(self.pickupDate, self.pickupOrDeliver, self.custName)
		return "{} - {}".format(nameStr, self.productStr)
	
	def clone(self):
		return order(self.orderRow)