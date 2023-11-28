import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from os.path import isfile
import time
import csv
import versioninfo


def isValidFile(filename : str):
	if (isfile(filename)) and (filename.endswith(".csv")):
		return True
	else:
		return False
	
class WPTT:
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
					myOrder = WPTT.order(orderRow)
					self.orders.append(myOrder)

	class window:
		class main:
			pass

		class loadFile:
			def __init__(self):
				self.frame = tk.Toplevel()

				lbl_instructions = tk.Label(
					self.frame,
					text="Enter the file to load. This can be downloaded from Square",
					width=80
				)
				lbl_instructions.pack(side=tk.TOP)

				frm_mid = tk.Frame(
					self.frame,
					height=1
				)
				frm_mid.pack()

				lbl_file	= tk.Label(
					frm_mid,
					text="File:",
					width=10
					)
				self.ent_file	= tk.Entry(
					frm_mid,
					width=60
				)
				btn_file	= tk.Button(
					frm_mid,
					text="Browse",
					command=self.selectFile,
					width=10
				)

				lbl_file.pack(
					fill=tk.Y,
					side=tk.LEFT
				)
				self.ent_file.pack(
					fill=tk.Y,
					side=tk.LEFT
				)
				btn_file.pack(
					fill=tk.Y,
					side=tk.LEFT
				)

				btn_continue	= tk.Button(
					self.frame,
					text="Load and continue",
					command=self.load
				)
				btn_continue.pack(side=tk.BOTTOM)
				self.frame.mainloop()

			def mainloop(self):
				self.frame.mainloop()

			def selectFile(self):
				filetypes = (
					('csv files', '*.csv'),
					('All files', '*.*')
				)

				filename = fd.askopenfilename(
					title='Open a file',
					filetypes=filetypes)
				self.ent_file.insert(0, filename)
				self.frame.lift()

			def load(self):
				# Check if file is valid
				# if not, pop up error
				# if valid, move to next screen
				if isValidFile(self.ent_file.get()):
					myOrders = WPTT.csvObj(self.ent_file.get())
					self.frame.destroy()
					updateMainWindow(myOrders)
				else:
					messagebox.showerror("Error!", "Invalid file!")

def updateMainWindow(orders : WPTT.importObj):
	global myOrders
	myOrders = orders
	updateFilters()
	tk_filterBy(None)

# ---------------------------------------------------------------------------- #
#                                                                              #
#                                   TKINTER                                    #
#                                                                              #
# ---------------------------------------------------------------------------- #

def tk_scroll_all_yview(*args):
	box_display_custEmail.yview(*args)
	box_display_name.yview(*args)
	box_display_date.yview(*args)
	box_display_product.yview(*args)

def tk_scroll_all_yscroll(*args):
	scr_displayOrders.set(*args)
	box_display_custEmail.yview_moveto(args[0])
	box_display_name.yview_moveto(args[0])
	box_display_date.yview_moveto(args[0])
	box_display_product.yview_moveto(args[0])

def tk_highlight_oNum(event):
	highlightBoxes(box_display_custEmail)

def tk_highlight_name(event):
	highlightBoxes(box_display_name)

def tk_highlight_date(event):
	highlightBoxes(box_display_date)

def tk_highlight_product(event):
	highlightBoxes(box_display_product)

def highlightBoxes(leaderBox):
	indicesToHighlight = leaderBox.curselection()
	box_display_custEmail.select_clear(0, tk.END)
	box_display_name.select_clear(0, tk.END)
	box_display_date.select_clear(0, tk.END)
	box_display_product.select_clear(0, tk.END)
	for index in indicesToHighlight:
		box_display_custEmail.selection_set(index)
		box_display_name.selection_set(index)
		box_display_date.selection_set(index)
		box_display_product.selection_set(index)

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
	box_display_custEmail.delete(0, tk.END)
	box_display_name.delete(0, tk.END)
	box_display_date.delete(0, tk.END)
	box_display_product.delete(0, tk.END)

def fillListBoxes(listOfOrders):
	global currentOrders
	currentOrders = listOfOrders
	for myOrder in listOfOrders:
		box_display_custEmail.insert(tk.END, myOrder.custEmail)
		box_display_name.insert(tk.END, myOrder.custName)
		box_display_date.insert(tk.END, myOrder.orderPlaced)
		box_display_product.insert(tk.END, myOrder.productStr)

def setupFilterListbox(rootframe, descriptor):
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
	box_filter.bind("<<ListboxSelect>>", tk_filterBy)
	return box_filter

def printOrders(orderList):
	if (len(orderList) == 0):
		messagebox.showerror("Printing...", "No orders selected! Cannot print")
		return
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
					time.strftime("%F %R", time.localtime()),
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
	whichcustEmails = [box_display_custEmail.get(index) for index in box_display_custEmail.curselection()]
	whichOrders = []
	for custEmail in whichcustEmails:
		for orderCandidate in myOrders.orders:
			if orderCandidate.custEmail == custEmail:
				whichOrders.append(orderCandidate)
				break
	printOrders(whichOrders)
		

root = tk.Tk()
root.title("Wonga Park Trees Tool - version {}".format(versioninfo.VERSION_STRING))
root.geometry("566x73")

menubar = tk.Menu(root)
filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="Load from file", command=WPTT.window.loadFile)
filemenu.add_command(label="Print all to PDF") #, command=donothing)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="File", menu=filemenu)

root.config(menu=menubar)

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

def enterFilterOptions(options, listbox, addAll = True):
	options.sort()
	if addAll:
		options = ["All"] + options
	for date in options:
		listbox.insert(tk.END, date)

def updateFilters():
	dateFilterOptions = list(set(x.pickupDate for x in myOrders.orders))
	enterFilterOptions(dateFilterOptions, box_date)
	fulfillmentOptions = ["Pickup", "Delivery"]
	enterFilterOptions(fulfillmentOptions, box_fulfillment)

def setupDisplayListbox(rootframe, descriptor, callbackFunc):
	frame = tk.Frame(rootframe)
	frame.pack(
		side=tk.LEFT,
		fill=tk.BOTH,
		expand=True
	)
	label = tk.Label(frame, text=descriptor)
	label.pack(
		side=tk.TOP,
		fill=tk.BOTH
	)
	box = tk.Listbox(
		frame,
		selectmode=tk.EXTENDED,
		exportselection=False
	)
	box.pack(
		side=tk.BOTTOM,
		fill=tk.BOTH,
		expand=True
	)
	box.bind("<<ListboxSelect>>", callbackFunc)
	return box

box_date = setupFilterListbox(frame_displayOrders, "Date")
box_fulfillment = setupFilterListbox(frame_displayOrders, "Pickup?")

box_display_custEmail	= setupDisplayListbox(frame_displayOrders, "Email", tk_highlight_oNum)
box_display_name		= setupDisplayListbox(frame_displayOrders, "Name", tk_highlight_name)
box_display_date		= setupDisplayListbox(frame_displayOrders, "Order placed on", tk_highlight_date)
box_display_product		= setupDisplayListbox(frame_displayOrders, "Product/s", tk_highlight_product)

scr_displayOrders = tk.Scrollbar(frame_displayOrders)
scr_displayOrders.pack(side=tk.RIGHT, fill=tk.BOTH)

box_display_custEmail.config(yscrollcommand=tk_scroll_all_yscroll)
box_display_name.config(yscrollcommand=tk_scroll_all_yscroll)
box_display_date.config(yscrollcommand=tk_scroll_all_yscroll)
box_display_product.config(yscrollcommand=tk_scroll_all_yscroll)
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

root.geometry("800x500")
root.mainloop()