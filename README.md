# Burrow
A client/browser that accesses _gopherspace_. It is under current early stage development.

 ![Burrow browser](http://brianmevans.com/files/burrow_01.png "Burrow v0.1.8 main window")

## Gopher
[_Gopher_](https://en.wikipedia.org/wiki/Gopher_(protocol)) is a communications protocol that, in the early 90s, competed (briefly) with what became the world wide web. _Gopher_ serves up files and text based menus. As such, it is much lighter weight than HTML documents and the like served over http. Due to its text based nature it also has the benefit of being reliable in its visual output and style, and for being relatively accessible. 

## Browser Features
The following is a list of current and future Burrow features:

- Graphical User Interface
    - Back/Forward buttons, move about in session history
    - Favorite button adds current page to favorites
    - Home, shows favorites and is a start page _(configurable)_
    - Address bar, on _ENTER_ submits a request for a _gopher_ page
    - Settings button, brings up configuration menu __(non-functional)__
    - Main window, displays request data/pages/files
    - Vertical scroll bar
    - A status bar to display various information
    - Links in menu pages behave similar to http style hyperlinks
    - Tabs __(non-functional)__

- Menus, Pages, and Files
    - Menus display clickable links
    - Text files display in the viewport
    - Image files display in the viewport
    - Downloadable images
    - Downloadable binaries/audio/video __(non-functional)__
    - HTML files, open in a new tab in the default web browser
    - Interactive pages/search display a search dialog and return a menu on send

- History
    - Session based history for backward and forward navigation
    - Persistent favorites
    - Record of last URL visited

- Application settings and menus
    - Settings menu __(non-functional)__
        - Color themes
        - Icon themes
        - History settings
        - Files/download settings
        - Toggle load into home vs. last visited
    - Secondary click context menus for favoriting, text manipulation, & file saving
    - Page saving for offline viewing
    
- Errors
    - Error warnings to user _(semi-functional)_
    - Error page on bad/malformed request _(semi-functional)_
    - Error display for type 3 server response _(semi-functional)_


## Installation

Burrow requires python3 to be installed on the system prior to running.
Until some bundling/setup-file creation occurs, you will also need to add:
    
    pip3 install pillow
    

On some linux distributions an additional package for tkinter may be required.
If you get a console error complaining about tkinter try the following (or equivalent for your package manager):

    sudo apt-get install python3-tk
    sudo apt-get install python3-pil.imagetk
    

## Distribution

Burrow's primary system target is debian based linux systems. Once a version 1.0 is reached the plan is to distribute via .DEB packages and possibly through snapcraft (if a workable bundle can be figured out).

Some version of windows executable may come along as well, depending on configurability of build tools (py2exe, freeze, etc) for windows executables and time.


## Contribute

To contribute, please branch off of `develop` and then submit a pull request into `develop` with any changes. As the project grows I will likely add wiki, issues, project, etc as the need arises and more people get involved.
