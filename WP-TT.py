import tkinter as tk
from tkinter import filedialog as fd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from os.path import isfile
import time
import csv
import itertools

class order:
	def __init__(self, orderRow: list):
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
		
		self.isDelivery		=	"DELIVER" in self.deliveryInstructions
		self.isPickup		=	not self.isDelivery
		self.pickupOrDeliver=	("Delivery" if self.isDelivery else "Pickup")
		

		self.productList	= []

		pickupDate			=	orderRow[8][:10]
		#convert US date to AU date
		self.pickupDate		=	pickupDate[3:6] + pickupDate[0:3] + pickupDate[6:10]
		product				=	orderRow[24]
		productQty			=	orderRow[23]
		productPrice		=	orderRow[29]
		productTotal		=	orderRow[30]

		self.productList.append((product, productQty, productPrice, productTotal))

		self.productStr = ", ".join(["{}x {}".format(x[1], x[0]) for x in self.productList])
	
	def __str__(self):
		nameStr = "{} : {} order for {}".format(self.pickupDate, self.pickupOrDeliver, self.custName)
		return "{} - {}".format(nameStr, self.productStr)

class csvObj:
	def __init__(self, filename : str):
		if filename is not None:
			self.filename = filename
			self.readOrdersFromFile(filename)

	def readOrdersFromFile(self, filename : str):
		with open(filename, newline='') as csvfile:
			orderList = csv.reader(csvfile, delimiter=',', quotechar='"')

			self.orders = []

			for orderRow in orderList:
				if orderRow[0] == 'Order':
					#if this is the description row, ignore it
					continue
				myOrder = order(orderRow)
				self.orders.append(myOrder)

def isValidFile(filename : str):
	if (isfile(filename)) and (filename.endswith(".csv")):
		return True
	else:
		return False

# ---------------------------------------------------------------------------- #
#                                                                              #
#                                   TKINTER                                    #
#                                                                              #
# ---------------------------------------------------------------------------- #

def tk_selectFile():
	filetypes = (
		('csv files', '*.csv'),
		('All files', '*.*')
	)

	filename = fd.askopenfilename(
		title='Open a file',
		filetypes=filetypes)
	ent_file.insert(0, filename)

def tk_initLoad():
	# Check if file is valid
	# if not, pop up error
	# if valid, move to next screen
	if isValidFile(ent_file.get()):
		frame_selectFile.quit()
		frame_selectFile.pack_forget()
	else:
		print("invalid file")

def tk_scroll_all_yview(*args):
	box_displayOrder_custEmail.yview(*args)
	box_displayOrder_name.yview(*args)
	box_displayOrder_date.yview(*args)
	box_displayOrder_product.yview(*args)

def tk_scroll_all_yscroll(*args):
	scr_displayOrders.set(*args)
	box_displayOrder_custEmail.yview_moveto(args[0])
	box_displayOrder_name.yview_moveto(args[0])
	box_displayOrder_date.yview_moveto(args[0])
	box_displayOrder_product.yview_moveto(args[0])

def tk_highlight_oNum(event):
	highlightBoxes(box_displayOrder_custEmail)

def tk_highlight_name(event):
	highlightBoxes(box_displayOrder_name)

def tk_highlight_date(event):
	highlightBoxes(box_displayOrder_date)

def tk_highlight_product(event):
	highlightBoxes(box_displayOrder_product)

def highlightBoxes(leaderBox):
	indicesToHighlight = leaderBox.curselection()
	box_displayOrder_custEmail.select_clear(0, tk.END)
	box_displayOrder_name.select_clear(0, tk.END)
	box_displayOrder_date.select_clear(0, tk.END)
	box_displayOrder_product.select_clear(0, tk.END)
	for index in indicesToHighlight:
		box_displayOrder_custEmail.selection_set(index)
		box_displayOrder_name.selection_set(index)
		box_displayOrder_date.selection_set(index)
		box_displayOrder_product.selection_set(index)

def tk_filterBy(event):
	# Get filtered items from listbox 1
	allowedDates = [box_date.get(index) for index in box_date.curselection()]
	# Get filtered items from listbox 2
	allowedFulfillments = [box_fulfillment.get(index) for index in box_fulfillment.curselection()]
	# Set displaylist to be those items
	displayItems = []
	for order in myOrders.orders:
		allowedDate = False
		allowedFulfil = False
		if (len(allowedDates) > 0):
			for date in allowedDates:
				if order.pickupDate == date or "All" == date:
					allowedDate = True
					break
		else:
			allowedDate = True
		if (len(allowedFulfillments) > 0):
			for fulfillment in allowedFulfillments:
				if order.pickupOrDeliver == fulfillment or "All" == fulfillment:
					allowedFulfil = True
					break
		else:
			allowedFulfil = True
		if (allowedDate and allowedFulfil):
			displayItems.append(order)
	emptyListBoxes()
	fillListBoxes(displayItems)

def emptyListBoxes():
	box_displayOrder_custEmail.delete(0, tk.END)
	box_displayOrder_name.delete(0, tk.END)
	box_displayOrder_date.delete(0, tk.END)
	box_displayOrder_product.delete(0, tk.END)

def fillListBoxes(listOfOrders):
	global currentOrders
	currentOrders = listOfOrders
	for myOrder in listOfOrders:
		box_displayOrder_custEmail.insert(tk.END, myOrder.custEmail)
		box_displayOrder_name.insert(tk.END, myOrder.custName)
		box_displayOrder_date.insert(tk.END, myOrder.orderPlaced)
		box_displayOrder_product.insert(tk.END, myOrder.productStr)

def filterListbox(rootframe, descriptor, filteroptions):
	thisFrame = tk.Frame(
		rootframe
	)
	thisFrame.pack(
		side=tk.LEFT,
		fill=tk.BOTH
	)
	lbl_column = tk.Label(
		thisFrame,
		text=descriptor
	)
	lbl_column.pack()
	box_filter = tk.Listbox(
		thisFrame,
		selectmode=tk.EXTENDED,
		exportselection=False
	)
	box_filter.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
	for date in filteroptions:
		box_filter.insert(tk.END, date)
	return box_filter

def printOrders(orderList):
	w, h = A4
	tmp = h
	h = w
	w = tmp
	margin = 36
	marginBottom = margin+108
	def printPicklist(printDoc):
		currentWritePosition = 0
		for order in orderList:
			if (currentWritePosition <= marginBottom):
				currentWritePosition = h-margin
				text = printDoc.beginText(margin, currentWritePosition)
				text.setFont("Courier", 12)
				text.textLine("{} - Picklist for {} orders".format(
					time.strftime("%F %R", time.gmtime()),
					len(orderList)
				))
				descriptionLine = "{:11s} | {:20s} | {:10s} | {:20s} | {:25s}".format(
					"Pickup Date",
					"Name",
					"Pickup?",
					"Phone Number",
					"Items"
				)
				text.textLine(descriptionLine)
				currentWritePosition -= 24
			pickLine = "{:11s} | {:20s} | {:10s} | {:20s} | {:25s}".format(
				order.pickupDate,
				order.custName,
				order.pickupOrDeliver,
				order.custPhone,
				order.productStr
			)
			text.textLine(pickLine)
			currentWritePosition -= 12
			if order.isDelivery:
				for line in order.deliveryInstructions.split("Delivery Instructions: "):
					text.textLine("    {}".format(line.replace("\n", " ")))
					currentWritePosition -= 12
			if (currentWritePosition <= marginBottom):
				printDoc.drawText(text)
				printDoc.showPage()

	def printInvoices(printDoc):
		#TODO
		print()

	def printToPdf():
		pdfFilename = "WP-TT-{}.pdf".format(int(time.time()))
		printDoc = canvas.Canvas(pdfFilename, pagesize=(w, h))
		if pickList.get():
			printPicklist(printDoc)
		if invoices.get():
			printInvoices(printDoc)
		printDoc.save()

	printDialogue = tk.Toplevel()
	printDialogue.title("Printing orders...")
	lbl_printDialogue = tk.Label(
		printDialogue,
		text="Printing {} orders".format(len(orderList)),
	)
	lbl_printDialogue.pack(side=tk.TOP)
	pickList = tk.BooleanVar()
	invoices = tk.BooleanVar()
	frame_pickList = tk.Frame(printDialogue)
	chk_pickList = tk.Checkbutton(frame_pickList, variable=pickList, onvalue=True, offvalue=False)
	lbl_pickList = tk.Label(frame_pickList, text="Print Picklist?")
	chk_pickList.pack(side=tk.LEFT)
	lbl_pickList.pack(side=tk.RIGHT)
	frame_pickList.pack(side=tk.TOP, fill=tk.BOTH)

	#TODO: FUTURE TASK
	"""
	frame_invoices = tk.Frame(printDialogue)
	chk_invoices = tk.Checkbutton(frame_invoices, variable=invoices, onvalue=True, offvalue=False)
	lbl_invoices = tk.Label(frame_invoices, text="Print Invoices?")
	chk_invoices.pack(side=tk.LEFT)
	lbl_invoices.pack(side=tk.RIGHT)
	frame_invoices.pack(side=tk.TOP, fill=tk.BOTH)
	"""
	btn_print = tk.Button(printDialogue, text="Print!", command=printToPdf)
	btn_print.pack(side=tk.BOTTOM)

	printDialogue.mainloop()

def printAll():
	printOrders(myOrders.orders)

def printFiltered():
	printOrders(currentOrders)

def printCurrent():
	whichcustEmails = [box_displayOrder_custEmail.get(index) for index in box_displayOrder_custEmail.curselection()]
	whichOrders = []
	for custEmail in whichcustEmails:
		for orderCandidate in myOrders.orders:
			if orderCandidate.custEmail == custEmail:
				whichOrders.append(orderCandidate)
				break
	printOrders(whichOrders)
		

root = tk.Tk()
root.title("Wonga Park Trees Tool")
root.geometry("566x73")

# Solicit file from user
frame_selectFile = tk.Frame(root)
frame_selectFile.pack()

lbl_instructions = tk.Label(
	frame_selectFile,
	text="Enter the file to load. This can be downloaded from Square",
	width=80
)
lbl_instructions.pack(side=tk.TOP)

frm_mid = tk.Frame(
	frame_selectFile,
	height=1
)
frm_mid.pack()

lbl_file	= tk.Label(
	frm_mid,
	text="File:",
	width=10
	)
ent_file	= tk.Entry(
	frm_mid,
	width=60
)
btn_file	= tk.Button(
	frm_mid,
	text="Browse",
	command=tk_selectFile,
	width=10
)

lbl_file.pack(
	fill=tk.Y,
	side=tk.LEFT
)
ent_file.pack(
	fill=tk.Y,
	side=tk.LEFT
)
btn_file.pack(
	fill=tk.Y,
	side=tk.LEFT
)

btn_continue	= tk.Button(
	frame_selectFile,
	text="Load and continue",
	command=tk_initLoad
)
btn_continue.pack(side=tk.BOTTOM)

root.mainloop()

# Load file, read all entries, display
myOrders = csvObj(ent_file.get())
frame_displayOrders = tk.Frame(root)
frame_displayOrders.pack(fill=tk.BOTH, expand=True)
lbl_displayOrders = tk.Label(
	frame_displayOrders,
	text="List of orders:",
	justify="left"
)
lbl_displayOrders.pack(side=tk.TOP)

frame_buttons = tk.Frame(frame_displayOrders, height=4)
frame_buttons.pack(side=tk.BOTTOM, fill=tk.X)

dateFilterOptions = list(set(x.pickupDate for x in myOrders.orders))
dateFilterOptions.sort()
dateFilterOptions = ["All"] + dateFilterOptions
box_date = filterListbox(frame_displayOrders, "Date", dateFilterOptions)
box_fulfillment = filterListbox(frame_displayOrders, "Pickup?", ["All", "Pickup", "Delivery"])
box_date.bind("<<ListboxSelect>>", tk_filterBy)
box_fulfillment.bind("<<ListboxSelect>>", tk_filterBy)

frame_displayOrder_custEmail = tk.Frame(frame_displayOrders)
frame_displayOrder_custEmail.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
lbl_displayOrder_custEmail	= tk.Label(frame_displayOrder_custEmail, text="Order Number")
box_displayOrder_custEmail		= tk.Listbox(
	frame_displayOrder_custEmail,
	selectmode=tk.EXTENDED,
	exportselection=False
)
lbl_displayOrder_custEmail.pack(side=tk.TOP, fill=tk.BOTH)
box_displayOrder_custEmail.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
box_displayOrder_custEmail.bind("<<ListboxSelect>>", tk_highlight_oNum)


frame_displayOrder_name = tk.Frame(frame_displayOrders)
frame_displayOrder_name.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
lbl_displayOrder_name		= tk.Label(frame_displayOrder_name, text="Name")
box_displayOrder_name		= tk.Listbox(
	frame_displayOrder_name,
	selectmode=tk.EXTENDED,
	exportselection=False
)
lbl_displayOrder_name.pack(side=tk.TOP, fill=tk.BOTH)
box_displayOrder_name.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

frame_displayOrder_date = tk.Frame(frame_displayOrders)
frame_displayOrder_date.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
lbl_displayOrder_date		= tk.Label(frame_displayOrder_date, text="Order placed on")
box_displayOrder_date		= tk.Listbox(
	frame_displayOrder_date,
	selectmode=tk.EXTENDED,
	exportselection=False
)
lbl_displayOrder_date.pack(side=tk.TOP, fill=tk.BOTH)
box_displayOrder_date.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

frame_displayOrder_product = tk.Frame(frame_displayOrders)
frame_displayOrder_product.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
lbl_displayOrder_product		= tk.Label(frame_displayOrder_product, text="Product/s")
box_displayOrder_product	= tk.Listbox(
	frame_displayOrder_product,
	selectmode=tk.EXTENDED,
	exportselection=False
)
lbl_displayOrder_product.pack(side=tk.TOP, fill=tk.BOTH)
box_displayOrder_product.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scr_displayOrders = tk.Scrollbar(frame_displayOrders)
scr_displayOrders.pack(side=tk.RIGHT, fill=tk.BOTH)

box_displayOrder_custEmail.config(yscrollcommand=tk_scroll_all_yscroll)
box_displayOrder_name.config(yscrollcommand=tk_scroll_all_yscroll)
box_displayOrder_date.config(yscrollcommand=tk_scroll_all_yscroll)
box_displayOrder_product.config(yscrollcommand=tk_scroll_all_yscroll)
scr_displayOrders.config(command=tk_scroll_all_yview)

btn_printall			= tk.Button(
	frame_buttons,
	text="Print all",
	command=printAll
)
btn_printCurrentFilters	= tk.Button(
	frame_buttons,
	text="Print current filters",
	command=printFiltered
)
btn_printCurrentSel		= tk.Button(
	frame_buttons,
	text="Print selected orders",
	command=printCurrent
)

btn_printall.pack(
	side=tk.LEFT,
	padx=5,
	pady=5
)
btn_printCurrentFilters.pack(
	side=tk.LEFT,
	padx=5,
	pady=5
)
btn_printCurrentSel.pack(
	side=tk.LEFT,
	padx=5,
	pady=5
)

fillListBoxes(myOrders.orders)

root.geometry("800x500")
root.mainloop()