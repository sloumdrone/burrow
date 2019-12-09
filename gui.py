#!/usr/bin/env python3

import tkinter as tk
import tkinter.simpledialog as dialog
from tkinter.filedialog import asksaveasfilename as savedialog
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
        self.read_config()
        self.conn = conn()
        self.parser = parser()
        self.search = None

        #colors
        self.FG = '#E0E2E4'
        self.BG = '#2F393C'
        self.LINK = '#E8E2B7'
        self.FLINK = '#93C763'
        self.ACTIVELINK = '#678CB1'
        self.HLB = '#804000'
        self.HLF = self.FG
        self.STATUS_BG = '#293134'
        self.STATUS_FG = '#FFCD22'
        self.ERROR = '#EC7600'
        self.BAR_BG = self.STATUS_BG
        self.BAR_FG = self.BG
        self.BAR_HLB = self.HLB
        self.BAR_HLF = self.FG
        self.BAR_SLOT = self.FG
        self.SCROLL = '#434A57'
        self.TYPES = '#A082BD'
        self.MENU_BG = self.BAR_BG
        self.MENU_FG = self.FG
        self.MENU_HLB = self.LINK
        self.MENU_HLF = self.BAR_BG

        #configure root window
        self.root = tk.Tk(className='Burrow')
        self.root.title('Burrow')
        sh = self.root.winfo_screenheight()
        sw = self.root.winfo_screenwidth()
        w = int(sw * 0.7)
        h = sh - 200
        self.root.geometry("{}x{}+{}+{}".format(w, h, sw//2-w//2, 50))
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
        self.site_display = tk.Text(self.body, bg=self.BG, foreground=self.FG, padx=20, pady=20, wrap=tk.WORD, state=tk.DISABLED, spacing2=2, spacing1=2, spacing3=2,  yscrollcommand=self.scroll_bar.set, highlightcolor=self.BG, highlightbackground=self.BAR_BG, relief=tk.FLAT, font="TkFixedFont")
        self.scroll_bar.config(command=self.site_display.yview, width=20, relief=tk.RIDGE)
        self.site_display.tag_configure('linkcolor', foreground=self.LINK, spacing1=5, spacing2=5, spacing3=5)
        self.site_display.tag_configure('favoritecolor', foreground=self.FLINK, spacing1=5, spacing2=5, spacing3=5)

        self.site_display.tag_configure('type_tag', background=self.BG, foreground=self.TYPES, spacing2=1, spacing1=1, spacing3=1)
        self.site_display.tag_configure('error_text', foreground=self.ERROR, spacing1=5, spacing2=5, spacing3=5)

        #status bar objects
        self.status_info = tk.Label(self.status_bar, textvariable=self.message_bar_content, bg=self.STATUS_BG, takefocus=0, fg=self.ACTIVELINK)

        #menu objects
        self.context_menu = tk.Menu(self.body, tearoff=0, bg=self.MENU_BG, fg=self.MENU_FG, activebackground=self.MENU_HLB, activeforeground=self.MENU_HLF, activeborderwidth=0)

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
        self.btn_back.bind('<ButtonRelease-1>', self.go_back)
        self.btn_forward.bind('<ButtonRelease-1>', self.go_forward)
        self.btn_home.bind('<ButtonRelease-1>', self.load_home_screen)
        self.site_display.bind("<Up>", lambda event: self.site_display.yview_scroll(-1, 'units'))
        self.site_display.bind("<Down>", lambda event: self.site_display.yview_scroll(1, 'units'))
        self.site_display.bind("<Button-1>", lambda event: self.site_display.focus_set())
        self.site_display.bind("k", lambda event: self.site_display.yview_scroll(-1, 'units'))
        self.site_display.bind("j", lambda event: self.site_display.yview_scroll(1, 'units'))
        self.site_display.bind("h", self.go_back)
        self.site_display.bind("l", self.go_forward)
        self.entry_url.bind("<Button-1>", lambda event: self.entry_url.focus_set())
        self.root.protocol('WM_DELETE_WINDOW', self.close_window)
        self.btn_favorite.bind("<Button-1>", self.add_to_favorites)
        self.site_display.tag_bind('generic_r_click', "<Button-3>", (lambda event, href=None: self.show_context_menu(event, href)))


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
        back = Image.open('./images/back.png')
        self.img_back = ImageTk.PhotoImage(back)
        forward = Image.open('./images/forward.png')
        self.img_forward = ImageTk.PhotoImage(forward)
        favorite = Image.open('./images/favorite.png')
        self.img_favorite = ImageTk.PhotoImage(favorite)
        home = Image.open('./images/home.png')
        self.img_home = ImageTk.PhotoImage(home)
        settings = Image.open('./images/settings.png')
        self.img_menu = ImageTk.PhotoImage(settings)
        self.message_bar_content = tk.StringVar()
        self.message_bar_content.set('Ready.')


    def show_context_menu(self, e, href=None):
        current_page = self.entry_url.get()
        self.context_menu.delete(0,20)
        #add navigation options
        if len(self.history) > 1 and self.history_location > 0:
            back = (lambda event=e: self.go_back(event))
            self.context_menu.add_command(label=" Back ", command=back)
        else:
            self.context_menu.add_command(label=" Back ", state=tk.DISABLED)
        if len(self.history) > 1 and self.history_location < len(self.history) - 1:
            forward = (lambda event=e: self.go_forward(event))
            self.context_menu.add_command(label=" Forward ", command=forward)
        else:
            self.context_menu.add_command(label=" Forward ", state=tk.DISABLED)
        refresh = (lambda event=e, link=current_page: self.handle_request(event, link, False))
        self.context_menu.add_command(label=" Refresh ", command=refresh)
        if current_page != 'home':
            home = (lambda event=e: self.load_home_screen(event))
            self.context_menu.add_command(label=" Home ", command=home)
        else:
            self.context_menu.add_command(label=" Home ", state=tk.DISABLED)
        save_as_file = (lambda data=self.site_display.get(1.0,tk.END), url=current_page: self.write_to_file(data, url))
        self.context_menu.add_command(label=" Save as... ", command=save_as_file)

        if href:
            self.context_menu.add_separator()
            copy_link = (lambda link=href: self.copy_to_clipboard(link))
            self.context_menu.add_command(label=" Copy URL to clipboard ", command=copy_link)

            if self.is_favorite(href):
                self.context_menu.add_separator()
                delete_favorite = (lambda event=e, link=href: self.remove_favorite(event, link))
                self.context_menu.add_command(label=" Delete from favorites ", command=delete_favorite)
                rename_favorite = (lambda event=e, link=href: self.rename_favorite(event, link))
                self.context_menu.add_command(label=" Rename this favorite ", command=rename_favorite)
            elif href:
                self.context_menu.add_separator()
                add_favorite = (lambda event=e, link=href: self.add_to_favorites(event, link))
                self.context_menu.add_command(label=" Add to favorites ", command=add_favorite)
        self.context_menu.tk_popup(e.x_root, e.y_root)


    def copy_to_clipboard(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)


    # ------------Start navigation methods---------------------------


    def handle_request(self,event=False, url=False, history=True):
        self.loading_bar = tk.Label(self.entry_url, text=' Loading... ', width=12, relief=tk.FLAT, height=1, fg='#FFFFFF', bg=self.TYPES)
        self.loading_bar.pack(side=tk.RIGHT, padx=(0,10))
        self.loading_bar.update_idletasks()

        url = url if url else self.entry_url.get()
        parsed_url = self.parse_url(url)

        if not parsed_url:
            if url == 'home':
                return self.load_home_screen(history)
            else:
                data = {'type': '3', 'body': '3ERROR: Improperly formatted URL\tfalse\tnull.host\t1\n'}
                # return False
        elif parsed_url['protocol'] == 'http://':
            wb.open(url,2,True)
            self.populate_url_bar(self.history[-1])
            self.loading_bar.destroy()
            return False

        self.populate_url_bar(url)

        if history:
            self.add_to_history(url)

        if parsed_url and parsed_url['type'] == '7':
            self.show_search()
            return False # display search
        elif not parsed_url:
            data = {'type': '3', 'body': '3ERROR: Improperly formatted URL\tfalse\tnull.host\t1\n'}
        else:
            data = self.execute_address(parsed_url)

        self.send_to_screen(data['body'],data['type'])


    def parse_url(self, url=False):
        parsed_url = self.parser.parse_url(url)

        if not parsed_url:
            return False

        return parsed_url


    def execute_address(self, url):
        response = self.conn.request(url['resource'], url['host'], url['type'], url['port'])

        if not response:
            # send error to screen
            print('ERROR in execute address...')
            return False


        # Get the data to the screen
        self.site_display.focus_set()
        self.config["last_viewed"] = url

        return response


    def add_to_history(self, url):
        self.history = self.history[:self.history_location+1]
        self.history.append(url)
        self.history_location = len(self.history) - 1



    def gotolink(self, event, href, tag_name):
        if href.find('URL:') >= 0:
            href = href.split('URL:')[1]
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
        data2 = self.load_favorites()
        link_count = self.send_to_screen(data, '1', True)
        self.send_to_screen(data2, '1', False)


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

        try:
            self.loading_bar.destroy()
        except:
            pass



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

        if clear:
            self.link_count = 0

        for x in data:
            if x['type'] == 'i':
                self.site_display.insert(tk.END,'        \t\t{}\n'.format(x['description']), ('generic_r_click'))
            elif x['type'] == '3':
                self.site_display.insert(tk.END,'        \t\t{}\n'.format(x['description']), ('generic_r_click'))
            elif x['type'] in types:
                # adapted from:
                # https://stackoverflow.com/questions/27760561/tkinter-and-hyperlinks
                if x['port'] and x['port'][0] != ':':
                    x['port'] = ':{}'.format(x['port'])

                link = 'gopher://{}{}/{}{}'.format(x['host'], x['port'], x['type'], x['resource'])

                tag_name = 'link{}'.format(self.link_count)
                callback = (lambda event, href=link, tag_name=tag_name: self.gotolink(event, href, tag_name))
                # favorite = [x for x in self.config['favorites'] if x['url'] == link]
                favorite = self.is_favorite(link)
                self.site_display.tag_bind(tag_name, "<Button-1>", callback)
                self.site_display.insert(tk.END, types[x['type']], ('type_tag',))
                self.site_display.insert(tk.END,'\t\t')
                callback_menu = (lambda event, href=link: self.show_context_menu(event, href))
                self.site_display.tag_bind(tag_name, '<Button-3>', callback_menu)

                if favorite:
                    styletag = 'favoritecolor'
                else:
                    styletag = 'linkcolor'

                hover = (lambda event, href=link, tag_name=tag_name: self.hoverlink(event, href, tag_name))
                clear = (lambda event, tag_name=tag_name: self.clear_status(event, tag_name))
                self.site_display.tag_bind(tag_name, "<Enter>", hover)
                self.site_display.tag_bind(tag_name, '<Leave>', clear)

                self.site_display.insert(tk.END, x['description'], (tag_name,styletag))
                self.site_display.insert(tk.END, '\n')
                self.link_count += 1
        self.site_display.config(state=tk.DISABLED)
        return self.link_count


    def show_text(self, data):
        if data[-2:] == '.\n':
            data = data[:-2]
        self.site_display.config(state=tk.NORMAL)
        self.site_display.delete(1.0, tk.END)
        self.site_display.insert(tk.END, data, 'generic_r_click')
        self.site_display.config(state=tk.DISABLED)


    def show_image(self, data):
        self.current_image = self.build_image(data)
        callback = (lambda event, image=data, write='wb': self.write_to_file(contents=image, event=event, write=write))
        hover = (lambda event, href='Download this image...', tag_name='image_download': self.hoverlink(event, href, tag_name))
        clear = (lambda event, tag_name='image_download': self.clear_status(event, tag_name))
        self.site_display.tag_bind('image_download', "<Button-1>", callback)
        self.site_display.tag_bind('image_download', "<Enter>", hover)
        self.site_display.tag_bind('image_download', '<Leave>', clear)
        self.site_display.config(state=tk.NORMAL)
        self.site_display.delete(1.0, tk.END)
        self.site_display.insert(tk.END,'Download this image',('linkcolor','image_download'))
        self.site_display.insert(tk.END, '\n\n')
        self.site_display.image_create(tk.END, image = self.current_image)
        self.site_display.config(state=tk.DISABLED)


    def show_bin_download(self, data):
        url = self.entry_url.get()
        filename = url.rpartition('/')
        if len(filename) > 1:
            filename = filename[-1]
        else:
            filename = ''

        callback = (lambda event, bindata=data, write='wb': self.write_to_file(contents=bindata, event=event, write=write))
        hover = (lambda event, href='Download {}'.format(filename), tag_name='bin_download': self.hoverlink(event, href, tag_name))
        clear = (lambda event, tag_name='bin_download': self.clear_status(event, tag_name))
        self.site_display.tag_bind('bin_download', "<Button-1>", callback)
        self.site_display.tag_bind('bin_download', "<Enter>", hover)
        self.site_display.tag_bind('bin_download', '<Leave>', clear)
        self.site_display.config(state=tk.NORMAL)
        self.site_display.delete(1.0, tk.END)
        self.site_display.insert(tk.END,'Download ')
        self.site_display.insert(tk.END,filename,('linkcolor','bin_download'))
        self.site_display.config(state=tk.DISABLED)


    def send_to_screen(self, data, itemtype='1', clear=True):
        if itemtype in ['0','h']:
            self.show_text(data)
        elif itemtype in ['1','3','7']:
            data = self.parser.parse_menu(data)
            self.show_menu(data, clear)
        elif itemtype in ['p','I','g']:
            self.show_image(data)
        elif itemtype in ['s','9','M','c',';','d','5']:
            self.show_bin_download(data)

        try:
            self.loading_bar.destroy()
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
        e.tag_config(tag_name, underline=1)
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

    def is_favorite(self, href):
        for val in self.config['favorites']:
            if val['url'] == href:
                return True
        return False


    def rename_favorite(self, event, link):
        index = None
        for ind, val in enumerate(self.config['favorites']):
            if val['url'] == link:
                index = ind
                break
        if index is not None:
            title = self.config['favorites'][index]['name']
            new_name = dialog.askstring("Rename favorite","\n     Change favorite name to:     \n".format(title), initialvalue=title)
            if new_name:
                self.config['favorites'][index]['name'] = new_name
                self.write_config(self.config)
                if self.entry_url.get() == 'home':
                    self.load_home_screen()
                return True
        return False


    def remove_favorite(self, event, href):
        index = None
        for ind, val in enumerate(self.config['favorites']):
            if val['url'] == href:
                index = ind
                break
        if index is not None:
            self.config['favorites'].pop(index)
            self.write_config(self.config)
        self.load_home_screen()


    def add_to_favorites(self, event, url=None):
        favorite_name = dialog.askstring("Add to favorites", "What would you like to title this favorite?")
        if url is None:
            url = self.entry_url.get()
        if not favorite_name or not url:
            return False
        favorite = {"url": url, "name": favorite_name}
        self.config["favorites"].append(favorite)
        self.write_config(self.config)
        if self.entry_url.get() == 'home':
            self.load_home_screen()
        return True


    def write_to_file(self, contents=None, page_url=None, event=None, write='w'):
        url = self.entry_url.get()
        filetype = url.rpartition('.')
        if len(filetype) > 1:
            filetype = filetype[-1]
        else:
            filetype = 'txt'

        filename = savedialog(initialdir="~/Desktop/", defaultextension='.{}'.format(filetype), title="Save As File", filetypes=((filetype,'*.{}'.format(filetype)),('all files','*.*')))
        if not filename or filename is None or contents is None:
            return False
        with open(filename, write) as f:
            f.write(contents)
        return True



if __name__ == '__main__':
    app = GUI()
    app.root.mainloop()


