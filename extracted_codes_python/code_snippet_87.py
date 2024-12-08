from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import sqlite3

PORT = 5001

class SimpleRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(bytes("<h1>African Gates Tours</h1>", "utf-8"))
        elif self.path == '/about':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(bytes("<h1>About Us</h1><p>We offer amazing tours!</p>", "utf-8"))
        elif self.path == '/api/tours':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            # ... (Implement logic to fetch tours from your database)
            tours = [
                {'tour_id': 1, 'tour_name': 'Safari Adventure', 'description': 'Explore the wild!', 'price': 500.00, 'capacity': 10, 'availability': '2024-07-15', 'tour_type': 'Adventure'},
                {'tour_id': 2, 'tour_name': 'Cultural Immersion', 'description': 'Experience local traditions', 'price': 300.00, 'capacity': 8, 'availability': '2024-07-20', 'tour_type': 'Cultural'}
            ]
            self.wfile.write(bytes(json.dumps(tours), "utf-8"))
        else:
            self.send_error(404, "Page Not Found")

    def do_POST(self):
        if self.path == '/api/book':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            booking_data = json.loads(post_data.decode('utf-8'))
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            # ... (Implement logic to process the booking)
            self.wfile.write(bytes(json.dumps({'message': 'Booking successful'}), 'utf-8'))
        else:
            self.send_error(404, "Page Not Found")

httpd = HTTPServer(('', PORT), SimpleRequestHandler)
print(f"Serving at http://localhost:{3306}")
httpd.serve_forever()
