import tkinter as tk
import versioninfo

from WPTT import mainWindow

if __name__ == "__main__":
	root = tk.Tk()
	root.title("Wonga Park Trees Tool - version {}".format(versioninfo.VERSION_STRING))
	root.geometry("800x500")

	userWindow = mainWindow.main(root)

	root.mainloop()