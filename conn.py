import socket
import sys
import re

class Tunnel:
    def __init__(self):
        self.raw_request = None
        self.text_output = None
        self.types = {
            '0': '(TXT)',
            '1': '(MENU)',
            '2': None,
            '3': 'Error code',
            '4': None,
            '5': None,
            '6': None,
            '7': '(INTER)',
            '8': '(TLNET)',
            '9': '(BIN)',
            '+': None,
            'g': '(GIF)',
            'I': '(IMG)',
            't': None,
            'h': '(HTML)',
            'i': '(INFO)',
            's': '(SOUND)'
        }


    def make_connection(self, resource, host, itemtype, port=70):
        endline = '\r\n'
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(30.0)
        try:
            port = int(port)
        except:
            port = 70
        s.connect((host, port))
        s.sendall((resource + '\r\n').encode('utf-8'))
        r = s.makefile(mode = 'r', errors='ignore')
        try:
            raw_data = r.read()
        except UnicodeDecodeError:
            raw_data = 'iError decoding server response :(\tfalse\tnull.host\t1'

        try:
            data = raw_data.decode('utf-8','ignore')
        except:
            data = raw_data

        self.raw_request = data

        if itemtype[1] == '1':
            #handle menus
            self.text_output = self.gopher_to_text(self.raw_request)
        elif itemtype[1] == '0':
            #handle text files
            self.text_output = [self.raw_request]
        self.text_output.insert(0,itemtype[1])
        s.close()
        return self.text_output



    def gopher_to_text(self, message):
        message = message.split('\n')
        message = [x.split('\t') for x in message]
        message = [{'type': x[0][0], 'description': x[0][1:], 'resource': x[1], 'host': x[2], 'port': x[3]} for x in message if len(x) >= 4]
        return message


    def parse_url(self, url):
        regex = r'^(?P<protocol>(?:gopher:\/\/)?)?(?P<host>[\w\.\d]+)(?P<port>(?::\d+)?)?(?P<type>(?:\/\d)?)?(?P<resource>(?:\/[\w\/\d\-?.]*)?)?$'
        match = re.match(regex, url)
        protocol = match.group('protocol')
        itemtype = match.group('type')
        host = match.group('host')
        port = match.group('port')
        resource = match.group('resource')

        if protocol != 'gopher://' and protocol:
            return False
        if itemtype and not self.types[itemtype[1]]:
            return False
        elif not itemtype:
            itemtype = '/1'
        if not host:
            return False
        if not resource:
            resource = '/'
        if port:
            port = port[1:]

        self.make_connection(resource, host, itemtype, port)


if __name__ == '__main__':
    inp = sys.argv[1:]
    if len(inp) >= 2:
        test = Tunnel()
        test.make_connection(inp[1],inp[0],'70')
    else:
        print('Incorrect request')
