#!/usr/bin/env python3

import tkinter as tk
from connect import connect as conn
from parser import parser
import time
import sys
import json
import os.path

class GUI:
    def __init__(self):
        self.history = []
        self.history_location = -1
        self.message_bar_content = ''
        self.config = None
        self.read_config()
        self.conn = conn()
        self.parser = parser()

        #colors
        self.FG = 'black'
        self.BG = 'white'
        self.LINK = 'blue'
        self.ACTIVELINK = 'red'
        self.HLB = '#e37800'
        self.HLF = 'white'
        self.STATUS = 'silver'
        self.ERROR = 'red'

        #create and configure root window
        self.root = tk.Tk(className='Digger')
        self.root.title('Digger')
        self.root.geometry("1200x800")
        self.add_assets()

        #main frame objects
        self.top_bar = tk.Frame(self.root, padx=10, height=70, relief=tk.FLAT, bd=2)
        self.body = tk.Frame(self.root, relief=tk.RIDGE, bd=2)
        self.status_bar = tk.Frame(self.root, height="20", bg=self.STATUS, takefocus=0)

        #top bar objects
        self.btn_back = tk.Button(self.top_bar, image=self.img_back, bd=0, highlightthickness=0, takefocus=1)
        self.btn_forward = tk.Button(self.top_bar,image=self.img_forward, bd=0, highlightthickness=0)
        self.btn_favorite = tk.Button(self.top_bar,image=self.img_favorite, bd=0, highlightthickness=0)
        self.btn_home = tk.Button(self.top_bar, image=self.img_home, bd=0, highlightthickness=0)
        self.entry_url = tk.Entry(self.top_bar, selectbackground=self.HLB, selectforeground=self.HLF, highlightcolor=self.HLB)
        self.btn_menu = tk.Button(self.top_bar, image=self.img_menu, bd=0, highlightthickness=0)

        #body objects
        self.scroll_bar = tk.Scrollbar(self.body)
        self.site_display = tk.Text(self.body, bg=self.BG, foreground=self.FG, padx=20, pady=20, wrap=tk.WORD, state=tk.DISABLED, spacing2=5, spacing1=5, yscrollcommand=self.scroll_bar.set)
        self.scroll_bar.config(command=self.site_display.yview, width=20, relief=tk.RIDGE)
        self.site_display.tag_configure('linkcolor', foreground=self.LINK, spacing1=5)
        self.site_display.tag_configure('type_tag', background=self.FG, foreground=self.BG, spacing2=0, spacing1=0)
        self.site_display.tag_configure('error_text', foreground=self.ERROR, spacing1=5, spacing2=5, spacing3=5)

        #status bar objects
        self.status_info = tk.Label(self.status_bar, textvariable=self.message_bar_content, bg=self.STATUS, takefocus=0)

        self.pack_geometry()
        self.add_status_titles()
        self.add_event_listeners()

        #load the home screen
        self.load_home_screen()

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
        self.entry_url.bind('<Return>', self.execute_address)
        self.btn_back.bind('<Button-1>', self.go_back)
        self.btn_forward.bind('<Button-1>', self.go_forward)
        self.btn_home.bind('<Button-1>', self.load_home_screen)
        self.site_display.bind("<Up>", lambda event: self.site_display.yview_scroll(-1, 'units'))
        self.site_display.bind("<Down>", lambda event: self.site_display.yview_scroll(1, 'units'))
        self.site_display.bind("<Button-1>", lambda event: self.site_display.focus_set())
        self.entry_url.bind("<Button-1>", lambda event: self.entry_url.focus_set())
        self.root.protocol('WM_DELETE_WINDOW', self.close_window)


    def pack_geometry(self):
        self.top_bar.pack(expand=False,fill=tk.BOTH,side=tk.TOP,anchor=tk.NW)
        self.top_bar.pack_propagate(False)
        self.body.pack(expand=True,fill=tk.BOTH,side=tk.TOP)
        self.status_bar.pack(expand=False,fill=tk.X,side=tk.TOP,anchor=tk.SW)
        self.btn_back.pack(side=tk.LEFT, padx=(0,20))
        self.btn_forward.pack(side=tk.LEFT, padx=(0,20))
        self.btn_home.pack(side=tk.LEFT, padx=(0,20))
        self.entry_url.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10, ipadx=10)
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
        self.img_back = tk.PhotoImage(file='./btn_back.png')
        self.img_forward = tk.PhotoImage(file='./btn_forward.png')
        self.img_favorite = tk.PhotoImage(file='./btn_refresh.png')
        self.img_menu = tk.PhotoImage(file='./btn_menu.png')
        self.img_home = tk.PhotoImage(file='./btn_home.png')
        self.img_menu = tk.PhotoImage(file='./btn_menu.png')
        self.message_bar_content = tk.StringVar()
        self.message_bar_content.set('Ready.')


    # ------------Start navigation methods----------------------------


    def execute_address(self, event=False, btn_url=False, history=True):
        url = btn_url if btn_url else self.entry_url.get()
        if url == 'home':
            self.load_home_screen()
            return True

        parsed_url = self.parser.parse_url(url)

        if not parsed_url:
            # To do: build errors class to handle displaying errors
            # return errors.url_error
            return False

        response = self.conn.request(self.parser.resource, self.parser.host, self.parser.filetype, self.parser.port)

        if not response:
            # To do: build errors class to handle displaying errors
            # return errors.connection_error_NUMBER
            return False

        if history:
            self.history = self.history[:self.history_location+1]
            self.history.append(url)
            self.history_location = len(self.history) - 1

        # Get the data to the screen
        self.site_display.focus_set()
        self.config["last_viewed"] = url

        self.send_to_screen(self.conn.raw_response, self.conn.filetype)
        return True


    def gotolink(self, event, href, tag_name):
        element = event.widget
        element.tag_config(tag_name, background=self.ACTIVELINK)
        element.update_idletasks()  # make sure change is visible
        time.sleep(.5)  # optional delay to show changed text
        self.entry_url.delete(0,tk.END)
        self.entry_url.insert(tk.END,href)
        success = self.execute_address()
        element.tag_config(tag_name, background=self.BG)  # restore tag text style
        element.update_idletasks()


    def load_home_screen(self,event=None):
        print('Loading home')
        with open('./home.gopher','r') as f:
            data = f.read()
        self.entry_url.delete(0, tk.END)
        self.entry_url.insert(tk.END, 'home')
        self.send_to_screen(data, '1')


    def go_back(self, event):
        if len(self.history) <= 1 and self.history_location <= 0:
            return False

        self.history_location -= 1
        href = self.history[self.history_location]
        self.populate_url_bar(href)
        self.execute_address(False, href, False)


    def go_forward(self, event):
        if len(self.history) <= 1 and self.history_location >= len(self.history) - 1:
            return False

        self.history_location += 1
        href = self.history[self.history_location]
        self.populate_url_bar(href)
        self.execute_address(False, href, False)


    #-------------Start view methods----------------


    def load_favorites(self):
        header = 'i#############\tfalse\tnull.host\t1\r\ni  manually edit in go.config.json\tfalse\tnull.host\t1\r\n or add using the favorites button\tfalse\tnull.host\t1\r\ni\tfalse\tnull.host\t1\r\n'
        #soon add code to load in favorites here
        self.send_to_screen(data=header, clear=False)

    def show_menu(self, data, clear=True):
        if not data:
            #error handling will go here
            return False

        types = {
                    '0': '( TEXT )',
                    '1': '( MENU )',
                    '3': '( ERROR)',
                    '7': '( INTR )',
                    '9': '( BIN  )',
                    'g': '( GIF  )',
                    'I': '( IMG  )',
                    'h': '( HTML )',
                    'i': '( INFO )',
                    's': '( SOUND)'
                }

        self.site_display.config(state=tk.NORMAL)

        if clear:
            self.site_display.delete(1.0, tk.END)
        print('---------------')
        print(data)
        for x in data[1:]:
            print(x)
            if x['type'] == 'i':
                self.site_display.insert(tk.END,'        \t\t{}\n'.format(x['description']))
            elif x['type'] == '3':
                self.site_display.insert(tk.END,'        \t\t{}\n'.format(x['description']))
            elif x['type'] in types:
                link_count = 0

                # adapted from:
                # https://stackoverflow.com/questions/27760561/tkinter-and-hyperlinks
                if x['port'] and x['port'][0] != ':':
                    x['port'] = ':{}'.format(x['port'])

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
        print('Showing text')
        self.site_display.config(state=tk.NORMAL)
        self.site_display.delete(1.0, tk.END)
        self.site_display.insert(tk.END, data)
        self.site_display.config(state=tk.DISABLED)


    def send_to_screen(self, data, itemtype='1', clear=True):
        if itemtype == '0':
            self.show_text(data)
        elif itemtype in ['1','3']:
            print('got to menu call')
            data = self.parser.parse_menu(data)
            self.show_menu(data, clear)


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
        e.tag_config(tag_name, underline=1)
        self.site_display.config(cursor="arrow")
        e.update_idletasks()


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


