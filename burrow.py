#!/usr/bin/env python3
################################################
## Burrow, a gopher client/browser
## - - - - - - - - - - - - - - - - - - - - - - -
##   Version 0.2.1
################################################

from gui import GUI


if __name__ == '__main__':
    app = GUI()
    app.root.mainloop()
