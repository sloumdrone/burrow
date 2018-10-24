import socket

class connect:
    def __init__(self):
        self.raw_response = None
        self.filetype = None

    def request(self, resource, host, itemtype, port=70):
        #connects to server and returns list with response type and body
        socket_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_conn.settimeout(20.0)
        socket_conn.connect((host, port))
        socket_conn.sendall((resource + '\r\n').encode('utf-8'))

        response = socket_conn.makefile(mode = 'r', errors = 'ignore')
        try:
            self.raw_response = response.read()
            self.filetype = itemtype
        except UnicodeDecodeError:
            self.raw_response = '3Error decoding server response\tfalse\tnull.host\t1'
            self.filetype = '3'

        socket_conn.close()

        return {'type': self.filetype, 'body': self.raw_response}
