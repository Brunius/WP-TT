import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox
from tkinter import ttk
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
A4_landscape = (A4[1], A4[0])
from reportlab.pdfbase.pdfmetrics import stringWidth
import time

from os.path import isfile
from math import floor
from webbrowser import open_new

from .importOrders import csvObj

def isValidFile(filename : str):
	if (isfile(filename)) and (filename.endswith(".csv")):
		return True
	else:
		return False
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
			myOrders = csvObj(self.ent_file.get())
			self.frame.destroy()
			self.mainWindow.update(myOrders)
		else:
			messagebox.showerror("Error!", "Invalid file!")

class printWindow:
	class checkbox_row:
		def setup_checkbox(self, rootFrame, descriptor):
			frame_checkbox = tk.Frame(rootFrame)
			frame_checkbox.pack(side=tk.LEFT)
			checkbox	= tk.Checkbutton(frame_checkbox)
			checkbox.pack(side=tk.LEFT)
			label		= tk.Label(frame_checkbox, text=descriptor)
			label.pack(side=tk.LEFT)
			return checkbox
		
		def trigNone(self):
			if (self.noneVar.get()):
				self.check_combined.deselect()
				self.check_delivery.deselect()
				self.check_pickup.deselect()
				self.check_combined.config(state=tk.DISABLED)
				self.check_delivery.config(state=tk.DISABLED)
				self.check_pickup.config(state=tk.DISABLED)
			else:
				self.check_combined.select()
				self.check_delivery.deselect()
				self.check_pickup.deselect()
				self.check_combined.config(state=tk.NORMAL)
				self.check_delivery.config(state=tk.NORMAL)
				self.check_pickup.config(state=tk.NORMAL)
		def __init__(self, rootFrame):
			self.noneVar		= tk.BooleanVar()
			self.combinedVar	= tk.BooleanVar(value=True)
			self.deliveryVar	= tk.BooleanVar()
			self.pickupVar		= tk.BooleanVar()
			self.check_none		= self.setup_checkbox(rootFrame, "None")
			self.check_combined	= self.setup_checkbox(rootFrame, "Combined")
			self.check_delivery	= self.setup_checkbox(rootFrame, "Delivery")
			self.check_pickup	= self.setup_checkbox(rootFrame, "Pickup")
			
			self.check_none.config(variable=self.noneVar, command=self.trigNone)
			self.check_combined.config(variable=self.combinedVar)
			self.check_delivery.config(variable=self.deliveryVar)
			self.check_pickup.config(variable=self.pickupVar)
		def get(self):
			filterItems = []
			if self.combinedVar.get():
				filterItems.append("All")
			if self.deliveryVar.get():
				filterItems.append("Delivery")
			if self.pickupVar.get():
				filterItems.append("Pickup")
			return filterItems
		
		def set(self, list):
			if list[0]:
				self.check_none.select()
			else:
				self.check_none.deselect()
			if list[1]:
				self.check_combined.select()
			else:
				self.check_combined.deselect()
			if list[2]:
				self.check_delivery.select()
			else:
				self.check_delivery.deselect()
			if list[3]:
				self.check_pickup.select()
			else:
				self.check_pickup.deselect()

	def setup_window(self):
		# Setup GUI
		self.frame = tk.Toplevel()
		self.frame.title("WPTT - Printing {} orders".format(len(self.orders)))
		frame_picklist = tk.Frame(self.frame)
		frame_picklist.pack(side=tk.TOP)
		tk.Label(frame_picklist, text="Print Picklists:").pack(side=tk.TOP, anchor=tk.W)
		self.checkbox_picklist = self.checkbox_row(frame_picklist)
		self.checkbox_picklist.set([False, True, True, True])
		ttk.Separator(self.frame, orient=tk.HORIZONTAL).pack(fill=tk.X)
		frame_tags = tk.Frame(self.frame)
		frame_tags.pack(side=tk.TOP)
		tk.Label(frame_tags, text="Print Tags:").pack(side=tk.TOP, anchor=tk.W)
		self.checkbox_tags = self.checkbox_row(frame_tags)
		ttk.Separator(self.frame, orient=tk.HORIZONTAL).pack(fill=tk.X)
		btn_print = tk.Button(self.frame, text="Print!", command=self.print)
		btn_print.pack(side=tk.BOTTOM)

	def __init__(self, ordersToPrint):
		if len(ordersToPrint) == 0:
			messagebox.showerror("Print Error", "No orders selected! Cannot print")
			return
		
		self.orders		= ordersToPrint
		self.pageSize	= A4_landscape
		self.margin		= 36		#36 = 1/2", roughly
		self.marginB	= 72		#This gives lots of room for the last order to print properly
		self.default_file_name	= time.strftime("Trees-%F-%H-%M.pdf", time.localtime())
		self.setup_window()
		
	def print_picklist(self, orderList, extradescriptor=""):
		w, h = self.pageSize
		setupFlag = True
		for index, order in enumerate(orderList):
			if (setupFlag):
				setupFlag = False
				text = self.canvas.beginText(self.margin, h-self.margin)
				text.setFont("Courier", 12)
				text.textLine("{} - Picklist for {} orders {}".format(
					time.strftime("%F %R", time.localtime()),
					len(orderList),
					extradescriptor
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
			if (text.getY() <= self.marginB) or (index+1 == len(orderList)):
				self.canvas.drawText(text)
				self.canvas.showPage()
				setupFlag = True
	
	def print_tags(self, orderList):
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
				#if (width > (virtPage[0]-self.margin*2)):
				#	newLine = textwrap.wrap(line, floor(virtPage[0]/charWidth))
				#	lines[index:index+len(newLine)-1] = newLine
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

		tagOrders = orderList
		for index, order in enumerate(tagOrders):
			if (order.productQty > 1):
				newOrderList = []
				for x in range(order.productQty):
					newOrder = order.clone()
					newOrder.productQty = 1
					newOrder.productStr = "{}x {}\n({} of {})".format(
						newOrder.productQty,
						newOrder.product,
						x+1,
						order.productQty
					)
					newOrderList.append(newOrder)
				tagOrders[index:index+len(newOrderList)-1] = newOrderList

		for index, order in enumerate(tagOrders):
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

		for filterItem in self.checkbox_picklist.get():
			if filterItem == "All":
				self.print_picklist(self.orders, "- All")
			else:
				orderList = []
				for order in self.orders:
					if filterItem == order.pickupOrDeliver:
						orderList.append(order)
				if (len(orderList) > 0):
					self.print_picklist(orderList, "- {}".format(filterItem))
		for filterItem in self.checkbox_tags.get():
			if filterItem == "All":
				self.print_tags(self.orders)
			else:
				orderList = []
				for order in self.orders:
					if filterItem == order.pickupOrDeliver:
						orderList.append(order)
				if (len(orderList) > 0):
					self.print_tags(orderList)

		# After all options are completed - save and close dialogue
		self.canvas.save()
		self.frame.destroy()

		# Open newly saved pdf
		open_new(self.saveas)