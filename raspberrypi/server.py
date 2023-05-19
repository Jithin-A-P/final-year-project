from http.server import BaseHTTPRequestHandler
import json

class Server(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass # override the log_message method to suppress log messages

    purchased_products = dict()
    products = open('labels.txt', 'r').read().splitlines()
    prices = [
        80.0,
        20.0,
        40.0
    ]
    upi_id = 'jithinap009@oksbi'
    data = {
        'products': products,
        'prices': prices,
        'upi_id': upi_id
    }

    def clear_products():
        Server.purchased_products = dict()    

    def add_product(product_idx: int, weight: int):
        if product_idx in Server.purchased_products:
            added_value = {product_idx: Server.purchased_products.get(product_idx) + weight}
        else:
            added_value = {product_idx: weight}
        Server.purchased_products.update(added_value)

    def do_GET(self):
        if self.path == '/purchased-products':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(Server.purchased_products).encode())
        elif self.path == '/data':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(Server.data).encode())
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == '/prices':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            post_data_dict = json.loads(post_data.decode('utf-8'))
            Server.prices = post_data_dict['prices']
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'post_data')
        else:
            self.send_error(404)
