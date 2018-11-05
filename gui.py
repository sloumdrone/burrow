#!/usr/bin/env python3

import tkinter as tk
import tkinter.simpledialog as dialog
from connect import connect as conn
from parser import parser
import time
import sys
import json
import os.path
from io import BytesIO
from PIL import Image, ImageTk
import webbrowser as wb

class GUI:
    def __init__(self):
        self.history = []
        self.history_location = -1
        self.message_bar_content = ''
        self.config = None
        self.read_config()
        self.conn = conn()
        self.parser = parser()
        self.search = None

        #colors
        self.FG = '#E0E2E4'
        self.BG = '#2F393C'
        self.LINK = '#E8E2B7'
        self.ACTIVELINK = '#678CB1'
        self.HLB = '#804000'
        self.HLF = '#E0E2E4'
        self.STATUS_BG = '#293134'
        self.STATUS_FG = '#FFCD22'
        self.ERROR = '#E8E2B7'
        self.BAR_BG = '#293134'
        self.BAR_FG = '#2F393C'
        self.BAR_HLB = '#804000'
        self.BAR_HLF = '#E0E2E4'
        self.BAR_SLOT = '#E0E2E4'
        self.SCROLL = '#434A57'
        self.TYPES = '#A082BD'


        #create and configure root window
        self.root = tk.Tk(className='Burrow')
        self.root.title('Burrow')
        self.root.geometry("1200x800")
        self.add_assets()

        #main frame objects
        self.top_bar = tk.Frame(self.root, padx=10, height=50, relief=tk.FLAT, bd=2, bg=self.BAR_BG)
        self.body = tk.Frame(self.root, relief=tk.FLAT, bd=0, bg=self.BG)
        self.status_bar = tk.Frame(self.root, height="20", relief=tk.FLAT, bg=self.STATUS_BG, takefocus=0)

        #top bar objects
        self.btn_back = tk.Button(self.top_bar, image=self.img_back, bd=0, highlightthickness=0, takefocus=1, bg=self.BAR_BG)
        self.btn_forward = tk.Button(self.top_bar,image=self.img_forward, bd=0, highlightthickness=0, bg=self.BAR_BG)
        self.btn_favorite = tk.Button(self.top_bar,image=self.img_favorite, bd=0, highlightthickness=0, bg=self.BAR_BG)
        self.btn_home = tk.Button(self.top_bar, image=self.img_home, bd=0, highlightthickness=0, bg=self.BAR_BG)
        self.entry_url = tk.Entry(self.top_bar, selectbackground=self.HLB, selectforeground=self.HLF, highlightcolor=self.FG, highlightbackground=self.BAR_BG,  fg=self.BAR_FG, bg=self.BAR_SLOT)
        self.btn_menu = tk.Button(self.top_bar, image=self.img_menu, bd=0, highlightthickness=0, bg=self.BAR_BG)

        #body objects
        self.scroll_bar = tk.Scrollbar(self.body, bg=self.BAR_BG, bd=0, highlightthickness=0, troughcolor=self.BG, activebackground=self.SCROLL, activerelief=tk.RAISED)
        self.site_display = tk.Text(self.body, bg=self.BG, foreground=self.FG, padx=20, pady=20, wrap=tk.WORD, state=tk.DISABLED, spacing2=2, spacing1=2, spacing3=2,  yscrollcommand=self.scroll_bar.set, highlightcolor=self.BG, highlightbackground=self.BAR_BG, relief=tk.FLAT)
        self.scroll_bar.config(command=self.site_display.yview, width=20, relief=tk.RIDGE)
        self.site_display.tag_configure('linkcolor', foreground=self.LINK, spacing1=5, spacing2=5, spacing3=5)
        self.site_display.tag_configure('type_tag', background=self.BG, foreground=self.TYPES, spacing2=1, spacing1=1, spacing3=1)
        self.site_display.tag_configure('error_text', foreground=self.ERROR, spacing1=5, spacing2=5, spacing3=5)

        #status bar objects
        self.status_info = tk.Label(self.status_bar, textvariable=self.message_bar_content, bg=self.STATUS_BG, takefocus=0, fg=self.ACTIVELINK)


        self.pack_geometry()
        self.add_status_titles()
        self.add_event_listeners()

        #load the home screen
        self.load_home_screen(1)

    #-----------Start GUI configuration-----------------------

    def add_event_listeners(self):
        buttons = [
            self.btn_back,
            self.btn_forward,
            self.btn_favorite,
            self.btn_home,
            self.btn_menu
        ]

        for x in buttons:
            x.bind('<Enter>', self.update_status)
            x.bind('<Leave>', self.clear_status)
            x.config(activebackground=self.BG)
        self.entry_url.bind('<Return>', self.handle_request)
        self.btn_back.bind('<Button-1>', self.go_back)
        self.btn_forward.bind('<Button-1>', self.go_forward)
        self.btn_home.bind('<Button-1>', self.load_home_screen)
        self.site_display.bind("<Up>", lambda event: self.site_display.yview_scroll(-1, 'units'))
        self.site_display.bind("<Down>", lambda event: self.site_display.yview_scroll(1, 'units'))
        self.site_display.bind("<Button-1>", lambda event: self.site_display.focus_set())
        self.entry_url.bind("<Button-1>", lambda event: self.entry_url.focus_set())
        self.root.protocol('WM_DELETE_WINDOW', self.close_window)
        self.btn_favorite.bind("<Button-1>", self.add_to_favorites)


    def pack_geometry(self):
        self.top_bar.pack(expand=False,fill=tk.BOTH,side=tk.TOP,anchor=tk.NW)
        self.top_bar.pack_propagate(False)
        self.body.pack(expand=True,fill=tk.BOTH,side=tk.TOP)
        self.status_bar.pack(expand=False,fill=tk.X,side=tk.TOP,anchor=tk.SW)
        self.btn_back.pack(side=tk.LEFT, padx=(0,20))
        self.btn_forward.pack(side=tk.LEFT, padx=(0,20))
        self.btn_home.pack(side=tk.LEFT, padx=(0,20))
        self.entry_url.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5, ipadx=10)
        self.btn_favorite.pack(side=tk.LEFT, padx=(10,10))
        self.btn_menu.pack(side=tk.LEFT)
        self.scroll_bar.pack(side=tk.RIGHT,fill=tk.Y)
        self.site_display.pack(expand=True, side=tk.TOP, fill=tk.BOTH)
        self.status_info.pack(side=tk.LEFT)


    def add_status_titles(self):
        self.btn_back.pop_title = 'Back'
        self.btn_forward.pop_title = 'Forward'
        self.btn_favorite.pop_title = 'Favorite'
        self.btn_home.pop_title = 'Home'
        self.btn_menu.pop_title = 'Menu'


    def add_assets(self):
        self.img_back = tk.PhotoImage(file='./images/back.png')
        self.img_forward = tk.PhotoImage(file='./images/forward.png')
        self.img_favorite = tk.PhotoImage(file='./images/favorite.png')
        self.img_home = tk.PhotoImage(file='./images/home.png')
        self.img_menu = tk.PhotoImage(file='./images/settings.png')
        self.message_bar_content = tk.StringVar()
        self.message_bar_content.set('Ready.')


    # ------------Start navigation methods----------------------------

    def handle_request(self,event=False, url=False, history=True):
        self.progress_bar = tk.Label(self.entry_url, text=' Loading... ', width=12, relief=tk.FLAT, height=1, fg='#FFFFFF', bg=self.TYPES)
        self.progress_bar.pack(side=tk.RIGHT, padx=(0,10))
        self.progress_bar.update_idletasks()

        url = url if url else self.entry_url.get()
        parsed_url = self.parse_url(url)

        if not parsed_url:
            if url == 'home':
                return self.load_home_screen(history)
            else:
                return False #error handling goes here

        self.populate_url_bar(url)

        if history:
            self.add_to_history(url)

        if parsed_url['type'] == '7':
            self.show_search()
            return False # display search
        else:
            data = self.execute_address(parsed_url)
            if not data:
                return False #error handling goes here

        self.send_to_screen(self.conn.raw_response,self.conn.filetype)



    def parse_url(self, url=False):
        parsed_url = self.parser.parse_url(url)

        if not parsed_url:
            # send error to screen
            print('Error parsing URL')
            return False

        return parsed_url


    def execute_address(self, url):
        response = self.conn.request(url['resource'], url['host'], url['type'], url['port'])

        if not response:
            # send error to screen
            return False


        # Get the data to the screen
        self.site_display.focus_set()
        self.config["last_viewed"] = url

        self.send_to_screen(self.conn.raw_response, self.conn.filetype)
        return True


    def add_to_history(self, url):
        self.history = self.history[:self.history_location+1]
        self.history.append(url)
        self.history_location = len(self.history) - 1



    def gotolink(self, event, href, tag_name):
        if href[:4] == 'http':
            wb.open(href, 2, True)
            return True
        element = event.widget
        element.tag_config(tag_name, background=self.ACTIVELINK)
        element.update_idletasks()  # make sure change is visible
        time.sleep(.5)  # optional delay to show changed text
        element.tag_config(tag_name, background=self.BG)  # restore tag text style
        element.update_idletasks()
        self.handle_request(False,href)


    def load_home_screen(self,event=False):
        with open('./home.gopher','r') as f:
            data = f.read()
        self.entry_url.delete(0, tk.END)
        self.entry_url.insert(tk.END, 'home')
        if event:
            self.add_to_history('home')
        data += self.load_favorites()
        self.send_to_screen(data, '1')


    def go_back(self, event):
        if len(self.history) <= 1 or self.history_location <= 0:
            return False

        self.history_location -= 1
        href = self.history[self.history_location]
        self.handle_request(False, href, False)


    def go_forward(self, event):
        if len(self.history) <= 1 or self.history_location >= len(self.history) - 1:
            return False

        self.history_location += 1
        href = self.history[self.history_location]
        self.handle_request(False, href, False)


    def add_to_favorites(self, event):
        favorite_name = dialog.askstring("Add to favorites", "What would you like to title this favorite?")
        url = self.entry_url.get()
        if not favorite_name or not url:
            return False
        favorite = {"url": url, "name": favorite_name}
        self.config["favorites"].append(favorite)
        self.write_config(self.config)



    #-------------Start view methods----------------


    def load_favorites(self):
        header = ''
        #soon add code to load in favorites here
        for x in self.config["favorites"]:
            url = self.parser.parse_url(x["url"])
            if not url:
                continue
            entry = '{}{}\t{}\t{}\t{}\n'.format(url['type'], x['name'], url['resource'], url['host'], url['port'])
            header += entry
        return header


    def show_search(self):
        text1 = ' __   ___       __   __\n/__` |__   /\  |__) /  ` |__|\n.__/ |___ /~~\ |  \ \__, |  |\n\n\nPlease enter your search terms and press the enter key:\n\n'
        self.search = tk.Entry(width='50')
        self.search.bind('<Return>', self.query_search_engine)
        self.site_display.config(state=tk.NORMAL)
        self.site_display.delete(1.0, tk.END)
        self.site_display.insert(tk.END,text1)
        self.site_display.window_create(tk.END,window=self.search)
        self.site_display.config(state=tk.DISABLED)
        self.search.focus_set()


    def query_search_engine(self, event):
        base_url = self.entry_url.get()
        base_url = base_url.replace('/7/','/1/',1)
        query = self.search.get()
        url = '{}\t{}'.format(base_url,query)
        self.populate_url_bar(url)
        self.handle_request(False, url)
        self.search = None


    def show_menu(self, data, clear=True):
        if not data:
            #error handling will go here
            return False

        types = {
                    '0': '( TXT )',
                    '1': '( MNU )',
                    '3': '( ERR )',
                    '7': '( INT )',
                    '9': '( BIN )',
                    'g': '( GIF )',
                    'I': '( IMG )',
                    'h': '( HTM )',
                    'i': '( INF )',
                    's': '( SND )',
                    'p': '( PNG )'
                }

        self.site_display.config(state=tk.NORMAL)

        if clear:
            self.site_display.delete(1.0, tk.END)

        link_count = 0

        for x in data[1:]:
            if x['type'] == 'i':
                self.site_display.insert(tk.END,'        \t\t{}\n'.format(x['description']))
            elif x['type'] == '3':
                self.site_display.insert(tk.END,'        \t\t{}\n'.format(x['description']))
            elif x['type'] in types:
                # adapted from:
                # https://stackoverflow.com/questions/27760561/tkinter-and-hyperlinks
                if x['port'] and x['port'][0] != ':':
                    x['port'] = ':{}'.format(x['port'])

                if x['type'] == 'h':
                    link = '{}/{}'.format(x['host'], x['resource'])
                    link = 'http://{}'.format(link.replace('//','/'))
                else:
                    link = 'gopher://{}{}/{}{}'.format(x['host'], x['port'], x['type'], x['resource'])

                tag_name = 'link{}'.format(link_count)
                callback = (lambda event, href=link, tag_name=tag_name: self.gotolink(event, href, tag_name))
                hover = (lambda event, href=link, tag_name=tag_name: self.hoverlink(event, href, tag_name))
                clear = (lambda event, tag_name=tag_name: self.clear_status(event, tag_name))
                self.site_display.tag_bind(tag_name, "<Button-1>", callback)
                self.site_display.tag_bind(tag_name, "<Enter>", hover)
                self.site_display.tag_bind(tag_name, '<Leave>', clear)
                self.site_display.insert(tk.END, types[x['type']], ('type_tag',))
                self.site_display.insert(tk.END,'\t\t')
                self.site_display.insert(tk.END, x['description'], (tag_name,'linkcolor'))
                self.site_display.insert(tk.END, '\n')
                link_count += 1

        self.site_display.config(state=tk.DISABLED)
        return True


    def show_text(self, data):
        if data[-2:] == '\n.':
            data = data[:-2]
        self.site_display.config(state=tk.NORMAL)
        self.site_display.delete(1.0, tk.END)
        self.site_display.insert(tk.END, data)
        self.site_display.config(state=tk.DISABLED)


    def show_image(self, data):
        self.current_image = self.build_image(data)
        self.site_display.config(state=tk.NORMAL)
        self.site_display.delete(1.0, tk.END)
        self.site_display.image_create(tk.END, image = self.current_image)
        self.site_display.config(state=tk.DISABLED)


    def send_to_screen(self, data, itemtype='1', clear=True):
        if itemtype == '0':
            self.show_text(data)
        elif itemtype in ['1','3','7']:
            data = self.parser.parse_menu(data)
            self.show_menu(data, clear)
        elif itemtype in ['p','I','g']:
            self.show_image(data)

        try:
            self.progress_bar.destroy()
        except:
            pass

    def update_status(self, event, href=False):
        if href:
            self.message_bar_content.set(href)
        else:
            self.message_bar_content.set(event.widget.pop_title)


    def clear_status(self, event, tag_name=False):
        if tag_name:
            e = event.widget
            e.tag_config(tag_name, underline=0)
            self.site_display.config(cursor='xterm')
            e.update_idletasks()
        self.message_bar_content.set('')


    def populate_url_bar(self, url):
        self.entry_url.delete(0, tk.END)
        self.entry_url.insert(tk.END, url)


    def hoverlink(self, event, href, tag_name):
        self.update_status(event, href)
        e = event.widget
        e.tag_config(tag_name, underline=1, foreground=self.LINK)
        self.site_display.config(cursor="arrow")
        e.update_idletasks()

    def build_image(self, bytes_str):
        stream = BytesIO(bytes_str)
        pilimage = Image.open(stream)
        tkimage = ImageTk.PhotoImage(pilimage)
        return tkimage



    #--------Start file handling methods------------


    def read_config(self, url='./go.config.json'):
        if not os.path.isfile(url):
            self.create_config()
        with open('./go.config.json', 'r') as f:
            config = f.read()
        config = json.loads(config)
        self.config = config


    def write_config(self, config, url='./go.config.json'):
        with open(url, 'w') as f:
            data = json.dumps(config)
            f.write(data)


    def create_config(self):
        config = {"favorites": [],"last_viewed": None}
        self.write_config(config)


    def close_window(self):
        self.write_config(self.config)
        self.root.destroy()



if __name__ == '__main__':
    app = GUI()
    app.root.mainloop()


