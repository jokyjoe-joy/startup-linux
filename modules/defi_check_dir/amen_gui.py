"""
AMEN-GUI by angrybear
A Modular Extendable Notification Graphical User Interface
"""
import tkinter as tk
import logging
version = '0.0.1'


colors = {
    'bg': '#22313F',
    'working_bg': '#34495E',
    'menu_bg': '#2C3E50',
    'button_hoover': '#67809F',
    'button_activebg': '#34495E',
    'button_activefg': '#67809F',
    'button_fg': '#19B5FE',
    'infobox_fb': '#95A5A6',
    'infobox_afb': '#DADFE1',
    'infobox_abg': '#2C3E50'
}

fonts = {
    'menu_normal': ('roboto.ttf', 9),
    'menu_medium': ('roboto.ttf', 10),
    'menu_large': ('roboto.ttf', 12),
    'infobox_normal': ('roboto.ttf', 8)
}

root = ""

def DestroyWindow():
	logging.info("Destroying notification window ...")
	root.destroy()
	


class MainWindow:
	def __init__(self, root, title, text_content, button1_content="", button2_content=""):
		self.root = root
		self.title = title
		self.text_content = text_content
		self.button1_content = button1_content
		self.button2_content = button2_content

		# Main Frame
		self.main_window = tk.Frame(root)
		self.main_window.config(bg=colors['bg'])
		self.main_window.pack(side='top', fill='both', expand=True)

		# Top Bar
		self.top_bar = tk.Frame(self.main_window)
		self.top_bar.config(bg=colors['bg'],height=24)
		self.top_bar.pack(side='top', fill='x', expand=False)

        # Bottom Infobox Frame
		self.infobox = tk.Frame(self.main_window)
		self.infobox.config(bg=colors['bg'],height=16)
		self.infobox.pack(side='bottom', fill='x', expand=False)

		# Working Frame
		self.working = tk.Frame(self.main_window)
		self.working.config(bg=colors['working_bg'])
		self.working.pack(side='top', fill='both', expand=True)

		self.topbar_widgets()
		self.infobox_widgets()
		self.workingframe_widgets()

	def infobox_widgets(self):
		if self.button1_content:
			# BUTTON 1
			button_1 = tk.Button(self.infobox)

			# TODO: Buttons having their own callback specified by user.
			def doButton1():
				DestroyWindow()
				exit()

			button_1.config(bd=0,bg=colors['bg'],activebackground=colors['button_hoover'],
							activeforeground=colors['infobox_afb'],text=self.button1_content,fg=colors['infobox_fb'],
							font='roboto 12',relief='flat',command=doButton1)

			if self.button2_content:
				button_1.pack(side='left', padx=40, pady=1)
			else:
				button_1.pack()

		if self.button1_content and self.button2_content:
			button_2 = tk.Button(self.infobox)

			def doButton2():
				DestroyWindow()
				exit()

			button_2.config(bd=0,bg=colors['bg'],activebackground=colors['button_hoover'],
							activeforeground=colors['infobox_afb'],text=self.button2_content,fg=colors['infobox_fb'],
							font='roboto 12',relief='flat',command=doButton2)


			button_2.pack(side='right', padx=40, pady=1)

	def workingframe_widgets(self):
		text_1 = tk.Label(self.working)
		text_1.config(bd=0,bg=colors['working_bg'],text=self.text_content,wraplength=300,justify=tk.CENTER,
						fg=colors['infobox_fb'],font=fonts['menu_normal'],relief='flat')
		text_1.pack(pady=10)

	def topbar_widgets(self):
		text_1 = tk.Label(self.top_bar)
		text_1.config(bd=0,bg=colors['bg'],text=self.title,wraplength=300,justify=tk.CENTER,
					fg=colors['infobox_fb'],font='roboto 14 bold',relief='flat',)		
		text_1.pack()


def _(title,text,button1Text="",button2Text=""):
	logging.info("Initiating notification with title '%s'.", title)
	global root
	root = tk.Tk()
	root.wm_minsize(width=100, height=100)
	root.configure(bg=colors['bg'])
	root.overrideredirect(1)
	root.wm_attributes('-type', 'splash')
	root.wm_attributes('-alpha', 0.95)
	root.title(title)
	root.config(bd=2)
	root.wm_resizable(False, False)

	# TODO: Specify height by user choice. Should remove lot of hardcoded values in widgets.
	w = 300 # width for the Tk root
	h = 200 # height for the Tk root

	# get screen width and height
	ws = root.winfo_screenwidth() # width of the screen
	hs = root.winfo_screenheight() # height of the screen

	# calculate x and y coordinates for the Tk root window
	x = (ws/1.085) - (w/2)
	y = (hs/1.104) - (h/2)

	# set the dimensions of the screen 
	# and where it is placed
	root.geometry('%dx%d+%d+%d' % (w, h, x, y))

	logging.info("Sending notification with title '%s' ...",title)
	main_frame = MainWindow(root,title=title,text_content=text,button1_content=button1Text,button2_content=button2Text)
	root.mainloop()

# Runtime
if __name__ == '__main__':
	_("AMEN","I have no idea what to say.\n\nDo you accept that?","Yes")