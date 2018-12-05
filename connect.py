import socket

class connect:
    def __init__(self):
        self.raw_response = None
        self.filetype = None

    def request(self, resource, host, itemtype, port=70):
        #connects to server and returns list with response type and body
        socket_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_conn.settimeout(15.0)

        try:
            socket_conn.connect((host, port))
            socket_conn.sendall((resource + '\r\n').encode('utf-8'))

            if itemtype in ['i','0','1','3']:
                response = socket_conn.makefile(mode = 'r', errors = 'ignore')
            else:
                response = socket_conn.makefile(mode = 'rb', errors = 'ignore')

            self.raw_response = response.read()
            self.filetype = itemtype
        except socket.timeout:
            print('Socket timeout')
            socket_conn.close()
            return {'type': '1', 'body': '3ERROR: Server request timed out\tfalse\tnull.host\t1'}
        except Exception as e:
            print('Misc socket error: ', e)
            socket_conn.close()
            return {'type': '1', 'body': '3ERROR: Unable to communicate with remote server\tfalse\tnull.host\t1'}

        socket_conn.close()

        return {'type': self.filetype, 'body': self.raw_response}
