import re

# Handles parsing gopher data:
# URLs, Menus 

class parser:

    def __init__(self):
        self.host = None
        self.resource = None
        self.filetype = None
        self.protocol = None
        self.port = None
        self.menu = None

    def parse_url(self, url):
        # Take in a URL and output a dict of the url parts
        if url == 'home':
            return False

        regex = r'^(?P<protocol>(?:(gopher|http):\/\/)?)?(?P<host>[\w\-\.\d]+)(?P<port>(?::\d+)?)?(?P<type>(?:\/[01345679gIhisp])?)?(?P<resource>(?:\/.*)?)?$'

        match = re.match(regex, url)

        if not match:
            return False

        try:
            protocol = match.group('protocol')
            itemtype = match.group('type')
            host = match.group('host')
            port = match.group('port')
            resource = match.group('resource')
        except:
            return False

        if not resource:
            resource = '/'

        if not itemtype:
            itemtype = '1'


        self.filetype = itemtype[len(itemtype) - 1] if itemtype else '1'
        self.protocol = protocol if protocol else 'gopher://'
        self.port = int(port[1:]) if port else 70
        self.host = host
        self.resource = resource

        return {'host': self.host, 'resource': self.resource, 'type': self.filetype, 'protocol': self.protocol, 'port': self.port}


    def parse_menu(self, text):
        # Take in text from connection and output a list
        # w/ objects representing each menu item

        message_list = text.split('\n')
        message_list = [x.split('\t') for x in message_list]
        message_list = [{'type': x[0][0], 'description': x[0][1:], 'resource': x[1], 'host': x[2], 'port': x[3]} for x in message_list if len(x) >= 4]
        self.menu = message_list

        return message_list

