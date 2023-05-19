from http.server import HTTPServer
from server import Server
import sys

if __name__ == '__main__':
    Server.add_product(0, 1500)
    Server.add_product(0, 100)
    Server.add_product(1, 120)
    Server.add_product(1, 18)
    Server.add_product(2, 102)
    httpd = HTTPServer(('0.0.0.0', 8000), Server)
    print('HTTP Server started on port 8000')
    httpd.serve_forever()