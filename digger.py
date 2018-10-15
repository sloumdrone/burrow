#!/usr/bin/env python3

import tkinter as tk
from conn import Tunnel as go
import time
import sys

class GUI:
    def __init__(self):
        self.history = []
        self.history_location = -1
        self.message_bar_content = ''

        #colors
        self.FG = 'black'
        self.BG = 'white'
        self.LINK = 'blue'
        self.ACTIVELINK = 'red'
        self.HLB = '#e37800'
        self.HLF = 'white'
        self.STATUS = 'silver'

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
        self.btn_refresh = tk.Button(self.top_bar,image=self.img_refresh, bd=0, highlightthickness=0)
        self.btn_home = tk.Button(self.top_bar, image=self.img_home, bd=0, highlightthickness=0)
        self.entry_url = tk.Entry(self.top_bar, selectbackground=self.HLB, selectforeground=self.HLF, highlightcolor=self.HLB)
        self.btn_menu = tk.Button(self.top_bar, image=self.img_menu, bd=0, highlightthickness=0)

        #body objects
        self.site_display = tk.Text(self.body, bg=self.BG, foreground=self.FG, padx=20, pady=20, wrap=tk.WORD, state=tk.DISABLED, spacing2=5, spacing1=5)
        self.site_display.tag_configure('linkcolor', foreground=self.LINK, spacing1=5)
        self.site_display.tag_configure('type_tag', background=self.FG, foreground=self.BG, spacing2=0, spacing1=0)

        #status bar objects
        self.status_info = tk.Label(self.status_bar, textvariable=self.message_bar_content, bg=self.STATUS, takefocus=0)

        self.pack_geometry()
        self.add_status_titles()
        self.add_event_listeners()

        #---------------------------------------------------

    def add_event_listeners(self):
        buttons = [
            self.btn_back,
            self.btn_forward,
            self.btn_refresh,
            self.btn_home,
            self.btn_menu
        ]

        for x in buttons:
            x.bind('<Enter>', self.update_status)
            x.bind('<Leave>', self.clear_status)
        self.entry_url.bind('<Return>', self.execute_address)
        self.btn_back.bind('<Button-1>', self.go_back)
        self.btn_forward.bind('<Button-1>', self.go_forward)


    def pack_geometry(self):
        self.top_bar.pack(expand=False,fill=tk.BOTH,side=tk.TOP,anchor=tk.NW)
        self.top_bar.pack_propagate(False)
        self.body.pack(expand=True,fill=tk.BOTH,side=tk.TOP)
        self.status_bar.pack(expand=False,fill=tk.X,side=tk.TOP,anchor=tk.SW)
        self.btn_back.pack(side=tk.LEFT, padx=(0,20))
        self.btn_forward.pack(side=tk.LEFT, padx=(0,20))
        self.btn_refresh.pack(side=tk.LEFT, padx=(0,20))
        self.btn_home.pack(side=tk.LEFT, padx=(0,20))
        self.entry_url.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10, ipadx=10)
        self.btn_menu.pack(side=tk.LEFT, padx=(10,0))
        self.site_display.pack(expand=True, side=tk.TOP, fill=tk.BOTH)
        self.status_info.pack(side=tk.LEFT)


    def add_status_titles(self):
        self.btn_back.pop_title = 'Back'
        self.btn_forward.pop_title = 'Forward'
        self.btn_refresh.pop_title = 'Refresh'
        self.btn_home.pop_title = 'Home'
        self.btn_menu.pop_title = 'Menu'


    def add_assets(self):
        self.img_back = tk.PhotoImage(file='./btn_back.png')
        self.img_forward = tk.PhotoImage(file='./btn_forward.png')
        self.img_refresh = tk.PhotoImage(file='./btn_refresh.png')
        self.img_menu = tk.PhotoImage(file='./btn_menu.png')
        self.img_home = tk.PhotoImage(file='./btn_home.png')
        self.img_menu = tk.PhotoImage(file='./btn_menu.png')
        self.message_bar_content = tk.StringVar()
        self.message_bar_content.set('Ready.')


    def execute_address(self, event, btn_url=False):
        if btn_url and btn_url != -1:
            url = btn_url
        elif btn_url and btn_url == -1:
            return
        else:
            url = self.entry_url.get()
            self.history = self.history[:self.history_location+1]
            self.history.append(url)
            self.history_location = len(self.history) - 1
        self.site_display.focus_set()
        request = go()
        request.parse_url(url)
        self.send_to_screen(request.text_output)


    def gotolink(self, event, href, tag_name):
        res = event.widget
        res.tag_config(tag_name, background=self.ACTIVELINK)  # change tag text style
        res.update_idletasks()  # make sure change is visible
        time.sleep(.5)  # optional delay to show changed text
        self.entry_url.delete(0,tk.END)
        self.entry_url.insert(tk.END,href)
        self.execute_address(0) #the zero is meaningless, but the function expects a param
        res.tag_config(tag_name, background=self.BG)  # restore tag text style
        res.update_idletasks()


    def hoverlink(self, event, href, tag_name):
        self.update_status(event, href)
        e = event.widget
        e.tag_config(tag_name, underline=1)
        e.update_idletasks()


    def send_to_screen(self, data):
        link_count = 0
        self.site_display.config(state=tk.NORMAL)
        self.site_display.delete(1.0, tk.END)
        types = {
            '0': '( TEXT )',
            '1': '( MENU )',
            '2': None,
            '3': 'Error code',
            '4': None,
            '5': None,
            '6': None,
            '7': '( INTR )',
            '8': 'Telnet',
            '9': '( BIN  )',
            '+': None,
            'g': '( GIF  )',
            'I': '( IMG  )',
            't': None,
            'h': '( HTML )',
            'i': '( INFO )',
            's': '( SOUND)'
        }

        if data[0] == '0':
            self.site_display.insert(tk.END, data[1])
        elif data[0] == '1':
            for x in data[1:]:
                if x['type'] == 'i':
                    self.site_display.insert(tk.END,'        \t\t{}\n'.format(x['description']))
                else:
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


    def update_status(self, event, href=False):
        if href:
            self.message_bar_content.set(href)
        else:
            self.message_bar_content.set(event.widget.pop_title)


    def clear_status(self, event, tag_name=False):
        if tag_name:
            e = event.widget
            e.tag_config(tag_name, underline=0)
            e.update_idletasks()
        self.message_bar_content.set('')


    def go_back(self, event):
        if len(self.history) > 1 and self.history_location > 0:
            self.history_location -= 1
            href = self.history[self.history_location]
            self.entry_url.delete(0, tk.END)
            self.entry_url.insert(tk.END, href)
        else:
            href = -1
        self.execute_address(False, href)


    def go_forward(self, event):
        if len(self.history) > 1 and self.history_location < len(self.history) - 1:
            self.history_location += 1
            href = self.history[self.history_location]
            self.entry_url.delete(0,tk.END)
            self.entry_url.insert(tk.END, href)
        else:
            href = -1
        self.execute_address(False, href)



if __name__ == '__main__':
    app = GUI()
    app.root.mainloop()


