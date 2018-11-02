import socket

class connect:
    def __init__(self):
        self.raw_response = None
        self.filetype = None

    def request(self, resource, host, itemtype, port=70):
        #connects to server and returns list with response type and body
        socket_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            socket_conn.connect((host, port))
            socket_conn.sendall((resource + '\r\n').encode('utf-8'))

            if itemtype in ['I','p','g']:
                response = socket_conn.makefile(mode = 'rb', errors = 'ignore')
            else:
                response = socket_conn.makefile(mode = 'r', errors = 'ignore')
        except:
            socket_conn.close()
            return False

        try:
            self.raw_response = response.read()
            self.filetype = itemtype
        except UnicodeDecodeError:
            self.raw_response = '3Error decoding server response\tfalse\tnull.host\t1'
            self.filetype = '3'

        socket_conn.close()

        return {'type': self.filetype, 'body': self.raw_response}
