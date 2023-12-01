import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
A4_landscape = (A4[1], A4[0])
from reportlab.pdfbase.pdfmetrics import stringWidth
from os.path import isfile
import time
import csv
from math import floor
import textwrap
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
			def scroll_all_yscroll(self, *args):
				self.scr_display.set(*args)
				for box in self.scrollBoxes:
					box.yview_moveto(args[0])

			def scroll_all_yview(self, *args):
				for box in self.scrollBoxes:
					box.yview(*args)

			def emptyListboxes(self):
				for box in self.scrollBoxes:
					box.delete(0, tk.END)

			def fillListboxes(self, items):
				self.currentOrders = items
				for myOrder in items:
					self.box_display_name.insert(tk.END, myOrder.custName)
					self.box_display_email.insert(tk.END, myOrder.custEmail)
					self.box_display_date.insert(tk.END, myOrder.orderPlaced)
					self.box_display_product.insert(tk.END, myOrder.productStr)

			def filterBy(self, *args):
				dates	= [self.box_date.get(index) for index in self.box_date.curselection()]
				fulfil	= [self.box_fulfillment.get(index) for index in self.box_fulfillment.curselection()]

				displayItems = []
				for order in myOrders.orders:
					allowedDate = False
					allowedFulfil = False
					if (len(dates) > 0):
						for date in dates:
							if order.pickupDate == date or "All" == date:
								allowedDate = True
								break
					else:
						allowedDate = True
					if (len(fulfil) > 0):
						for fulfillment in fulfil:
							if order.pickupOrDeliver == fulfillment or "All" == fulfillment:
								allowedFulfil = True
								break
					else:
						allowedFulfil = True
					if (allowedDate and allowedFulfil):
						displayItems.append(order)
				self.emptyListboxes()
				self.fillListboxes(displayItems)

			def enterFilterOptions(self, options, listbox, addAll = True):
				listbox.delete(0, tk.END)
				options.sort()
				if addAll:
					options = ["All"] + options
				for opt in options:
					listbox.insert(tk.END, opt)

			def updateFilters(self):
				dateFilterOptions	= list(set(x.pickupDate for x in myOrders.orders))
				fulfillmentOptions	= ["Pickup", "Delivery"]
				self.enterFilterOptions(dateFilterOptions, self.box_date)
				self.enterFilterOptions(fulfillmentOptions, self.box_fulfillment)

			def menu_loadFile(self):
				WPTT.window.loadFile(self)

			def click_loadFile(self, *args):
				WPTT.window.loadFile(self)

			def setup_menubar(self, rootWindow):
				menubar = tk.Menu(rootWindow)

				filemenu = tk.Menu(menubar, tearoff=0)
				filemenu.add_command(label="Load from file", command=self.menu_loadFile)
				filemenu.add_command(label="Print all to PDF") #, command=donothing)
				filemenu.add_separator()
				filemenu.add_command(label="Exit", command=rootWindow.quit)

				menubar.add_cascade(label="File", menu=filemenu)
				return menubar
			
			def setup_filterListbox(self, rootFrame, descriptor):
				newFrame = tk.Frame(rootFrame)
				newFrame.pack(
					side=tk.LEFT,
					fill=tk.BOTH
				)
				label = tk.Label(
					newFrame,
					text=descriptor
				)
				label.pack()
				box = tk.Listbox(
					newFrame,
					selectmode=tk.EXTENDED,
					exportselection=False
				)
				box.pack(
					side=tk.LEFT,
					fill=tk.BOTH,
					expand=True
				)
				box.bind("<<ListboxSelect>>", self.filterBy)
				return box

			def setup_displayListbox(self, rootFrame, descriptor, callbackFunc):
				frame = tk.Frame(rootFrame)
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
				box.config(yscrollcommand=self.scroll_all_yscroll)
				self.scrollBoxes += [box]
				return box

			def lb_hl_boxes(self, leaderBox):
				indicesToHighlight = leaderBox.curselection()
				for box in self.scrollBoxes:
					box.select_clear(0, tk.END)
					for index in indicesToHighlight:
						box.selection_set(index)

			def lb_hl_email(self, event):
				self.lb_hl_boxes(self.box_display_email)

			def lb_hl_name(self, event):
				self.lb_hl_boxes(self.box_display_name)

			def lb_hl_date(self, event):
				self.lb_hl_boxes(self.box_display_date)

			def lb_hl_product(self, event):
				self.lb_hl_boxes(self.box_display_product)

			def setup_listboxes(self, rootFrame):
				self.box_date				= self.setup_filterListbox(rootFrame, "Date")
				self.box_fulfillment		= self.setup_filterListbox(rootFrame, "Pickup?")

				self.scrollBoxes = []
				self.box_display_email		= self.setup_displayListbox(rootFrame, "Email", self.lb_hl_email)
				self.box_display_name		= self.setup_displayListbox(rootFrame, "Name", self.lb_hl_name)
				self.box_display_date		= self.setup_displayListbox(rootFrame, "Order placed on", self.lb_hl_date)
				self.box_display_product	= self.setup_displayListbox(rootFrame, "Product/s", self.lb_hl_product)

				self.scr_display			= tk.Scrollbar(rootFrame)
				self.scr_display.pack(
					side=tk.RIGHT,
					fill=tk.BOTH
				)

			def setup_warning(self, rootFrame):
				self.warning = tk.Label(
					rootFrame,
					text="No file loaded! Click here to load one",
					highlightbackground="red",
					highlightthickness=2,
					padx=5,
					pady=5
				)
				self.warning.place(
					relwidth=0.4,
					relx=0.3,
					relheight=0.2,
					rely=0.4
				)
				self.warning.bind("<Button-1>", self.click_loadFile)

			def print_all(self):
				WPTT.window.print(myOrders.orders)

			def print_filter(self):
				WPTT.window.print(self.currentOrders)
				
			def print_selected(self):
				orderIndices = [index for index in self.box_display_name.curselection()]
				whichOrders = []
				for index in orderIndices:
					for candidate in myOrders.orders:
						# If we had an order number to compare, that would be better. Unfortunately, we don't.
						if ((candidate.custName == self.box_display_name.get(index)) and 
		  					(candidate.orderPlaced == self.box_display_date.get(index)) and
							(candidate.productStr == self.box_display_product.get(index))):
							whichOrders.append(candidate)
							break
				WPTT.window.print(whichOrders)

			def setup_singleButton(self, rootFrame, descriptor, callbackFunc):
				button = tk.Button(
					rootFrame,
					text=descriptor,
					command=callbackFunc
				)
				button.pack(
					side=tk.LEFT,
					padx=5,
					pady=5
				)

			def setup_printButtons(self, rootFrame):
				btn_printall			= self.setup_singleButton(rootFrame, "Print all", self.print_all)
				btn_printCurrentFilters	= self.setup_singleButton(rootFrame, "Print current filters", self.print_filter)
				btn_printSelection		= self.setup_singleButton(rootFrame, "Print selection", self.print_selected)

			def __init__(self, rootWindow):
				menubar = self.setup_menubar(rootWindow)
				rootWindow.config(menu=menubar)

				label_top = tk.Label(
					rootWindow,
					text="List of orders:",
					justify="left"
				)
				label_top.pack(
					side=tk.TOP
				)

				self.frame_display = tk.Frame(rootWindow)
				self.frame_display.pack(
					fill=tk.BOTH,
					expand=True
				)

				self.frame_buttons = tk.Frame(rootWindow)
				self.frame_buttons.pack(
					side=tk.BOTTOM,
					fill=tk.X
				)

				self.setup_listboxes(self.frame_display)
				self.setup_warning(self.frame_display)
				self.setup_printButtons(self.frame_buttons)

			def update(self, orders):
				global myOrders
				myOrders = orders
				mainWindow.updateFilters()
				mainWindow.filterBy(None)
				self.warning.destroy()

		class loadFile:
			def __init__(self, mainWindow):
				self.mainWindow = mainWindow
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
					self.mainWindow.update(myOrders)
				else:
					messagebox.showerror("Error!", "Invalid file!")
		
		class print:
			def __init__(self, ordersToPrint):
				if len(ordersToPrint) == 0:
					messagebox.showerror("Print Error", "No orders selected! Cannot print")
					return
				self.orders		= ordersToPrint
				self.pageSize	= A4_landscape

				self.margin		= 36		#36 = 1/2", roughly
				self.marginB	= 72		#This gives lots of room for the last order to print properly

				self.default_file_name	= time.strftime("Trees-%F-%H-%M.pdf", time.localtime())

				# Setup GUI
				self.frame = tk.Toplevel()
				self.frame.title("Printing orders...")
				lbl_printDialogue = tk.Label(
					self.frame,
					text="Printing {} orders".format(len(self.orders)),
				)
				lbl_printDialogue.pack(side=tk.TOP)
				"""
				pickList = tk.BooleanVar()
				invoices = tk.BooleanVar()
				frame_pickList = tk.Frame(self.frame)
				chk_pickList = tk.Checkbutton(frame_pickList, variable=pickList, onvalue=True, offvalue=False)
				lbl_pickList = tk.Label(frame_pickList, text="Print Picklist?")
				chk_pickList.pack(side=tk.LEFT)
				lbl_pickList.pack(side=tk.RIGHT)
				frame_pickList.pack(side=tk.TOP, fill=tk.BOTH)
				"""
				#TODO: FUTURE TASK
				"""
				frame_invoices = tk.Frame(printDialogue)
				chk_invoices = tk.Checkbutton(frame_invoices, variable=invoices, onvalue=True, offvalue=False)
				lbl_invoices = tk.Label(frame_invoices, text="Print Invoices?")
				chk_invoices.pack(side=tk.LEFT)
				lbl_invoices.pack(side=tk.RIGHT)
				frame_invoices.pack(side=tk.TOP, fill=tk.BOTH)
				"""
				btn_print = tk.Button(self.frame, text="Print!", command=self.print)
				btn_print.pack(side=tk.BOTTOM)

			def print_picklist(self):
				w, h = self.pageSize
				setupFlag = True
				for index, order in enumerate(self.orders):
					if (setupFlag):
						setupFlag = False
						text = self.canvas.beginText(self.margin, h-self.margin)
						text.setFont("Courier", 12)
						text.textLine("{} - Picklist for {} orders".format(
							time.strftime("%F %R", time.localtime()),
							len(self.orders)
						))
						descriptionLine = "{:11s} | {:20s} | {:10s} | {:20s} | {:25s}".format(
							"Pickup Date",
							"Name",
							"Pickup?",
							"Phone Number",
							"Items"
						)
						text.textLine(descriptionLine)
					pickLine = "{:11s} | {:20s} | {:10s} | {:20s} | {:25s}".format(
						order.pickupDate,
						order.custName,
						order.pickupOrDeliver,
						order.custPhone,
						order.productStr
					)
					text.textLine(pickLine)
					for line in order.deliveryInstructions.split("Delivery Instructions: "):
						if (len(line) > 0) and not (line.isspace()):
							text.textLine("    {}".format(line.replace("\n", " ")))
					if (text.getY() <= self.marginB) or (index+1 == len(self.orders)):
						self.canvas.drawText(text)
						self.canvas.showPage()
						setupFlag = True
			
			def print_tags(self):
				def setupPage(virtPage, pageSize):
					self.canvas.setFontSize(24)
					pageW, pageH = pageSize
					pageW = int(pageW)
					pageH = int(pageH)
					virtW, virtH = virtPage
					virtW = int(virtW)
					virtH = int(virtH)
					for x in range(0, pageW, virtW):
						self.canvas.line(x, 0, x, pageH)
					for y in range(0, pageH, virtH):
						self.canvas.line(0, y, pageW, y)
				
				def drawTag(virtPage, location_X : int, location_Y : int, orderString : str):
					lineSpacing	= 1.2
					fontName	= self.canvas._fontname
					fontSize	= self.canvas._fontsize
					lineSpacing	= fontSize*lineSpacing

					# This is worst case char width - it may not be this bad
					charWidth	= stringWidth("m", fontName, fontSize)
					
					lines		= orderString.splitlines()
					#If lines are longer than would fit, split into multiple lines
					for index, line in enumerate(lines):
						width = stringWidth(line, fontName, fontSize)
						if (width > virtPage[0]):
							newLine = textwrap.wrap(line, floor(virtPage[0]/charWidth))
							lines[index:index+len(newLine)-1] = newLine

					centre_X	= (location_X + 0.5) * virtPage[0]
					centre_Y	= (location_Y + 0.5) * virtPage[1]

					draw_X		= centre_X
					draw_Y		= (
						centre_Y - 
						(len(lines)/2)*lineSpacing
					)
					# Lines have to be reversed due to how they're interpreted in the for loop
					lines.reverse()
					for index, line in enumerate(lines):
						self.canvas.drawCentredString(draw_X, draw_Y+lineSpacing*index, line)

				w, h = self.pageSize
				numTags = 8
				# 8 = 4X, 2Y
				num_X = 4
				num_Y = 2
				virtPage = (w/num_X, h/num_Y)
				orderFormat = "{name}\n{product}\n{fulfillment}\n{date}"
				for index, order in enumerate(self.orders):
					orderString = orderFormat.format(
						name=order.custName,
						product=order.productStr,
						fulfillment=order.pickupOrDeliver,
						date=order.pickupDate,
					)
					if (index % numTags == 0):
						setupPage(virtPage, self.pageSize)
					index_X = (index % num_X)
					index_Y = (floor((index % numTags)/num_X))
					drawTag(virtPage, index_X, index_Y, orderString)
					if (index % numTags == numTags-1):
						self.canvas.showPage()

			def print(self):
				filetypes = (
					('pdf files', '*.pdf'),
					('All files', '*.*')
				)
				self.saveas = fd.asksaveasfilename(
					defaultextension="pdf",
					initialfile=self.default_file_name,
					filetypes=filetypes
				)
				if self.saveas is None:
					messagebox.showerror("Error!", "Print dialogue cancelled - nothing was saved")
					return
				self.canvas		= canvas.Canvas(self.saveas, pagesize=self.pageSize)
				# If picklist is desired - print it
				self.print_picklist()
				# If tags are desired - print them
				self.print_tags()

				# After all options are completed - save and close dialogue
				self.canvas.save()
				self.frame.destroy()

root = tk.Tk()
root.title("Wonga Park Trees Tool - version {}".format(versioninfo.VERSION_STRING))
root.geometry("800x500")

mainWindow = WPTT.window.main(root)

root.mainloop()