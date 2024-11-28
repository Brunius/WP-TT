import tkinter as tk

from .supportWindows import loadFile, printWindow

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
		loadFile(self)

	def click_loadFile(self, *args):
		loadFile(self)

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
		printWindow(myOrders.orders)
	def print_filter(self):
		printWindow(self.currentOrders)
		
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
		printWindow(whichOrders)

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
		global userWindow
		myOrders = orders
		self.updateFilters()
		self.filterBy(None)
		self.warning.destroy()