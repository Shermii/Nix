# A START OF SOMETHING TRULY HORRIBLE
import re
import os
import sys
import threading
import requests
from bs4 import BeautifulSoup

from gr import *
from widgets import *
from handlers import *
from highlighter import *

def wrap(func):
	def wrapped_func(*args, **kwargs):
		ret = func(*args, **kwargs)
		return ret

	return wrapped_func

# I have no idea why I did it this way
# Like sure it's kinda extendable and you can kinda add new functions easily, but it's like really fucking annoying
# I'll remake it someday, probably, maybe, hopefully, not really
# I have like 4 more things to remake and I am lazy

def ld(s, t, n):
	if (n >= 25): return 25
	n += 1
	if not s: return len(t)
	if not t: return len(s)
	if s[0] == t[0]: return ld(s[1:], t[1:], n)
	l1 = ld(s, t[1:], n)
	l2 = ld(s[1:], t, n)
	l3 = ld(s[1:], t[1:], n)
	if (n >= 25): return 25
	return 1 + min(l1, l2, l3)

class PARSER:
	def __init__(self, parent):
		""" OOP GONE WRONG NOT CLICKBAIT I HATE THIS """
		# this really is completely utterly shit and it's really badly extensible if you want to write an extra library or something
		# I have no idea how to make this extensible
		self.parent = parent

		# if you want to add more functions to react with widgets of the main window you'll have to write a "wrapper" for them in here
		# becuase if you do something like 
		# self.commands = {
			# "replace_tab": self.parent.buffer.replace_tabs,
		# }
		# then it will only work with the text widget that was referenced at the time of declaration of this class

		self.commands = { 
			"help": self.help,
			"highlighting": self.highlighting_set,
			"suggest": self.suggest_set,
			r"([0-9]+)|(^l[0-9]+$)|(^l[0-9]+.[0-9]+$)": self.l,
			"lget": self.l_get,
			"word_count(_get)*": self.word_count_get,
			"fget|fsize|file_size": self.file_size_get,
			"lyrics": self.lyrics_get,
			"temp": self.temp,
			"time": self.time_set,
			"blink": self.blink,
			"split": self.split,
			"unsplit": self.unsplit,
			"q|quit": self.win_quit,
			"sharpness": self.sharpness_set,
			"alpha|transparency": self.alpha_set,
			"convert": self.convert,
			"cap": self.video_capture,
			"screenshot|printscreen": self.screenshot,
			"resize": self.win_resize,
			"buffers": self.buffer_list,
			"(buffer_)*close": self.buffer_close,
			"save": self.file_save,
			"saveas": self.file_saveas,
			"open|load": self.file_load,
			"reopen|reload": self.file_reload,
			"rm|del": self.file_delete,
			"play": self.music_play,
			"pause": self.music_pause,
			"unpause": self.music_unpause,
			"stop": self.music_stop,
			"sys": self.system_execute,
			"exec": self.python_execute,
			"buffer_exec|bexec": self.buffer_execute,
			"ls|dir": self.ls,
			"cd": self.cd,
			"mkdir|new_dir(ectory)": self.new_directory,
			"rmdir|rm_dir(ectory)": self.delete_directory,
			"theme": self.theme,
			"retro": self.retro,
			"tab_size|set_tab|set_tab_size": self.tab_size_set,
			"flashy": self.parent.flashy_loading_bar,
			"replace_space(s*)": self.replace_spaces,
			"replace_tab(s*)": self.replace_tabs,
			"init": self.initialize_file,
			"del_empty_files": self.delete_empty_files,
			"lex": self.lex,
			"lex_print": self.lex_print,
			"lexer": self.lexer_switch,
			"tag(_add)*": self.add_tag,
			"tag_remove": self.remove_tag,
			"lf": self.lf,
			"crlf": self.crlf,
			"toggle_filebar": self.toggle_buffer_tab_show,
			"make": self.make,
			"config|config_file": self.open_config_file,
			"keybindings|keybinds": self.open_keybindings_file,
		}
		
	def parse_argument(self, arg=None):
		# O(n) somethign because fuck speed all I want is trash features
		for key in self.commands.keys():
			if (re.match(f"\\b({key})\\b", arg[0])):
				self.command_execute = self.commands[key]
				self.command_execute(arg)
				break
		else:
			self.command_execute = self.command_not_found
			self.command_execute(arg)

	def execute(self, arg=None):
		pass

	def help(self, arg=None):
		try:
			self.parent.command_out_set(f"{self.commands[arg[1]]}")
		except IndexError:
			x = ""
			for item in list(self.commands.keys()):
				x += "\n"+item
			self.parent.command_out_set(x)

	def highlighting_set(self, arg=None):
		if (arg[1] == "on"):
			self.parent.notify("highlighting on")
			self.parent.highlight_chunk()
			self.parent.highlighting = True
		elif (arg[1] == "off"):
			self.parent.unhighlight_chunk()
			self.parent.notify("highlighting off")
			self.parent.highlighting = False

	def suggest_set(self, arg=None):
		self.parent.suggest = not self.parent.suggest

	# elif (re.match(r"[0-9]", arg[0][0])):
		# self.txt.mark_set(tkinter.INSERT, float(arg[0]))
		# self.txt.see(float(arg[0])+2)
		# self.command_out_set(f"moved to: {float(arg[0])}")

	# elif (re.match(r"^l[0-9]+$|^l[0-9]+.[0-9]+$|^lget$", arg[0])):
	def l(self, arg=None):
		arg = "".join(arg)
		if (arg[0] == "l"): arg = arg[1:]
		if (len(arg.split(".")) < 2): arg = float(arg)
		index = self.parent.buffer.index(arg)
		self.parent.buffer.mark_set("insert", index)
		self.parent.buffer.see(index)
		self.parent.notify(f"moved to: {index}")

	def l_get(self, arg=None):
		self.parent.notify(f"{self.parent.buffer.get_line_count()}")

	def word_count_get(self, arg=None):
		self.parent.notify(f"{self.parent.buffer.get_word_count()}")

	def file_size_get(self, arg=None) -> None:
		self.parent.notify(f"buffer size: {len(self.parent.buffer.get('1.0', 'end-1c'))}B >>>> file size: {os.path.getsize(self.parent.buffer.full_name)}B")

	def lyrics_get(self, arg=None):
		def lyr():
			command1 = ""
			for word in arg[1:]:
				command1 += "-"+word
			command1 = command1.split(",")
			url = f"http://www.songlyrics.com/{command1[0]}/{command1[1]}-lyrics/"
			html = requests.get(url).content #gets the html of the url
			lyrics = BeautifulSoup(html, features="html.parser").find(id="songLyricsDiv").text
			self.parent.command_out_set(lyrics)
		threading.Thread(target=lyr).start()

	def temp(self, arg=None):
		self.parent.get_temperature()
		self.parent.buffer.focus_set()

	def time_set(self, arg=None):
		self.parent.notify(self.parent.get_time(), tags=[["1.0", "end"]])

	def blink(self, arg=None): #wonky as fuck
		if (arg[1] == "on"):
			for buffer in self.parent.file_handler.buffer_list:
				buffer[0]["insertontime"] = 500
				buffer[0]["insertofftime"] = 500

		elif (arg[1] == "off"):
			for buffer in self.parent.file_handler.buffer_list:
				buffer[0]["insertontime"] = 1
				buffer[0]["insertofftime"] = 0

		else:
			self.parent.notify(f"ERROR: Invalid argument {arg[1:]}", tags=[["1.0", "1.7"]])
			
		self.parent.buffer.focus_set()

	def split(self, arg=None): #also wonky as fuck
		if (arg[1] == "n"):
			self.unsplit(arg)

		elif (arg[1] == "vertical" or arg[1] == "v"):
			self.parent.split_mode = "vertical"
			self.parent.notify("split vertically")

		elif (arg[1] == "horizontal" or arg[1] == "h"):
			self.parent.split_mode = "horizontal"
			self.parent.notify("split horizontally")

		try:
			self.parent.buffer_render_index += 1
			self.parent.file_handler.load_buffer(buffer_index=self.parent.buffer.buffer_index+1)
		except IndexError: pass

		self.parent.reposition_widgets()

	def unsplit(self, arg=None):
		del self.parent.buffer_render_list[1: -1]
		self.parent.split_mode = "nosplit"
		self.parent.buffer_render_index = 0
		self.parent.reposition_widgets()

	def win_quit(self, arg=None):
		self.parent.run = False
		self.parent.quit()
		# self.destroy()

	def sharpness_set(self, arg=None):
		self.parent.sharpness = arg[1]
		self.parent.tk.call("tk", "scaling", arg[1])
		self.parent.notify(f"sharpness: {arg[1]}")

	def alpha_set(self, arg=None):
		if (arg[1] == "default"): arg[1] = 90
		self.parent.wm_attributes("-alpha", int(arg[1])/100)
		self.parent.notify(f"alpha: {arg[1]}")

	def convert(self, arg=None):
		try:
			if (arg[1][:2] == "0x"):
				decimal = int(arg[1], 16)
			elif (arg[1][:2] == "0b"):
				decimal = int(arg[1], 2)
			else:
				decimal = int(arg[1], 10)

			self.parent.notify(f"DECIMAL: {decimal}, HEXADECIMAL: {hex(decimal)}, BINARY: {bin(decimal)}")
		except ValueError:
			self.parent.notify("Error: wrong format; please, add prefix (0x | 0b)")

	def video_capture(self, arg=None):
		if (arg[1] == "start"):
			self.parent.process = self.parent.video_handler.video_record_start(self.parent)
		
		elif (arg[1] == "stop"):
			self.parent.video_handler.video_record_stop(self.parent.process)
			self.parent.notify("screen capture terminated")
	
	def screenshot(self, arg=None):
		self.parent.video_handler.screenshot(self)
	
	def win_resize(self, arg=None):
		self.parent.update_win()
		self.parent.geometry(f"{int(arg[1])}x{int(arg[2])}")
		
	def buffer_list(self, arg=None):
		if (not arg[1:]):
			self.parent.file_handler.list_buffer()
		else:
			self.parent.file_handler.load_buffer(arg[1:])

	def buffer_close(self, arg=None):
		self.parent.file_handler.close_buffer()

	def file_save(self, arg=None):
		self.parent.file_handler.save_file()
	
	def file_saveas(self, arg=None):
		self.parent.file_handler.save_file_as(filename=arg[1])

	def file_load(self, arg=None):
		self.parent.file_handler.load_file(filename="".join(arg[1:]))

	def file_reload(self, arg=None):
		self.parent.file_handler.load_file(filename=self.file_handler.current_file.name)

	def file_delete(self, arg=None):
		self.parent.file_handler.del_file(filename="".join(arg[1:]))
		
	def music_play(self, arg=None):
		self.parent.music_player.load_song(arg[1:])

	def music_pause(self, arg=None):
		self.parent.music_player.pause_song()

	def music_unpause(self, arg=None):
		self.parent.music_player.pause_song(unpause=True)

	def music_stop(self, arg=None):
		self.parent.music_player.stop_song()

	def system_execute(self, arg=None):
		self.parent.buffer.run_subprocess(argv=arg[1:])

	def python_execute(self, arg=None):
		print("ARGS: ", " ".join(arg[1:]))
		exec(" ".join(arg[1:]))

	def buffer_execute(self, arg=None):
		arg = self.parent.buffer.get("1.0", "end-1c")
		exec(arg)

	def ls(self, arg=None):
		self.parent.file_handler.ls(arg)

	def cd(self, arg=None):
		if (str(arg[1:])[0] == "/"):
			path = os.path.normpath(arg[1])
		else:
			path = os.path.normpath(f"{self.parent.file_handler.current_dir}/{arg[1]}")
			
		if (os.path.isdir(path)):
			self.parent.file_handler.current_dir = path
			self.parent.notify(arg=f"current directory: {self.parent.file_handler.current_dir}")
		else:
			self.parent.notify(arg=f"Error: File/Directory not found")

	def new_directory(self, arg=None):
		if (arg[1:]):
			self.parent.file_handler.new_directory(filename=arg[1])
		else:
			self.parent.notify("error: no name specified")

	def delete_directory(self, arg=None):
		if (arg[1:]):
			self.parent.file_handler.delete_directory(filename=arg[1])
		else:
			self.parent.notify("error: no name specified")

	def theme(self, arg=None):
		if (arg[1:]):
			self.parent.theme_set(arg[1:])
		else:
			self.parent.command_out.change_ex(self.parent.theme_set)
			result = ""
			for key in self.parent.theme_options.keys():
				result += key+"\n"
			self.parent.command_out_set(result, [["1.0", "end"]])

	def retro(self, arg=None):
		if (self.parent.font_family[0] != "Ac437 IBM VGA 9x8"): self.parent.font_set(retro=True)
		else: self.parent.font_set(retro=False) # retro is turned off by default so there is no need to actually put retro=False in the parameters, but I think it's more readable this way

	def tab_size_set(self, arg=None):
		if (arg[1:]):
			self.parent.conf["tab_size"] = int(arg[1])
			self.parent.buffer.configure_self()
			self.parent.notify(f"Current size: {self.parent.conf['tab_size']}")
		else:
			self.parent.notify(f"please, specify new size. Current size: {self.parent.conf['tab_size']}")

	def replace_spaces(self, arg=None):
		self.parent.buffer.replace_x_with_y(" "*self.parent.conf["tab_size"], "\t")

	def replace_tabs(self, arg=None):
		self.parent.buffer.replace_x_with_y("\t", " "*self.parent.conf["tab_size"])

	def initialize_file(self, arg=None):
		for init in list(self.parent.buffer.highlighter.language_init.keys()):
			if (re.match(init, self.parent.buffer.highlighter.lang)):
				self.parent.buffer.insert("1.0", self.parent.buffer.highlighter.language_init[init])
				break

			self.parent.highlight_chunk()

	def delete_empty_files(self, arg=None): #TODO
		pass

	def lex(self, arg=None):
		self.parent.buffer.lexer.lex()

	def lex_print(self, arg=None):
		self.parent.buffer.lexer.print_res()

	def lexer_switch(self, arg=None): # TEMPORARY UNTIL I COMPLETELY IMPLEMENT LEXERS
		if (arg[1].lower() == "python"):
			self.parent.buffer.lexer = LEXER(self.parent, self.parent.buffer)
		elif (arg[1].lower() == "c"):
			self.parent.buffer.lexer = C_LEXER(self.parent, self.parent.buffer)

	def add_tag(self, arg=None):
		index = self.parent.precise_index_sort(self.parent.buffer.index("insert"), self.parent.selection_start_index)
		self.parent.buffer.tag_raise(arg[1])
		self.parent.buffer.tag_add(arg[1], index[0], index[1])

	def remove_tag(self, arg=None):
		index = self.parent.precise_index_sort(self.parent.buffer.index("insert"), self.parent.selection_start_index)
		self.parent.buffer.tag_remove(arg[1], index[0], index[1])

	def lf(self, arg=None):
		self.parent.convert_to_lf()

	def crlf(self, arg=None):
		self.parent.convert_to_crlf()

	def toggle_buffer_tab_show(self, arg=None):
		self.parent.conf["show_buffer_tab"] = not self.parent.conf["show_buffer_tab"]
		self.parent.reposition_widgets()

	def make(self, arg=None):
		self.system_execute("sys make".split())

	def open_config_file(self, arg=None):
		self.parent.file_handler.load_file(filename=f"{os.path.dirname(__file__)}/config")
	
	def open_keybindings_file(self, arg=None):
		self.parent.file_handler.load_file(filename=f"{os.path.dirname(__file__)}/keybinds_conf.json")

	def command_not_found(self, arg=None):
		res = ""
		for c in arg:
			res += c+" "
		self.parent.notify(f"command <{res[:-1]}> not found", [["1.0", "1.7"], [f"1.{8+len(res)+2}", "end"]])





