# This server serves the webpages. It does not interact with the websockets.

import string, cgi, time
import json
from os import curdir, sep
from http.server import BaseHTTPRequestHandler, HTTPServer

# This is a simple http server and is not very safe in its current form.
# No encryption is offered and a clever user could access any file on your system with this setup.
class MyHandler(BaseHTTPRequestHandler):

    # Handles GET requests
    # PATH is the request path including the leading /
    # By default will just act as a base server and return files
    def do_GET(self):
        try:
            out = None
            if self.path == '/':
                self.path = "/index.html"
            if self.path == '/host':
                self.path == '/host.html'
            if self.path[0:4] == "/lib":
                self.path = "/vendor" + self.path[4:]

            qInd = self.path.find("?")
            if (qInd >= 0):
                request = self.path[qInd:]
                self.path = self.path[:qInd]
            if self.path == '/userFunc':
                out = userFunc()
                contentType = "json"
            if out is None:
                ext = self.path.split('.')
                ext = ext[len(ext)-1]
                read = 'rb'
                with open(curdir + sep + self.path, read) as f:
                    out = f.read()
                contentType = ext
            self.gen_headers(contentType)
            self.wfile.write(out)
            return
        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    # Generates headers for the given content type
    # Possible values are html, css, js, and json
    # Invalid values default to html
    def gen_headers(self, contentType):
        self.send_response(200)
        contentType = 'text/html'
        if (ext == "css"):
            contentType = 'text/css'
        elif (ext == "js"):
            contentType = 'application/javascript'
        elif (ext == "json"):
            contentType = 'application/json'
        self.send_header('Content-type', contentType)
        self.end_headers()

    # Handles POST requests
    # PATH is the request path including the leading /
    # body is a dictionary of the JSON body of the POST
    def do_POST(self):
        path = self.path[4:]
        length = int(self.headers['Content-Length'])
        body = json.loads(self.rfile.read(length).decode("utf-8"))       
        self.send_response(200)
        return

# User defined function. Returns json.
def userFunc():
    return '{"name": "PyWebPlug"}'

# A manual header parser
def parseHeaders(headers):
    headers = headers.split('\n')
    out = {}
    for header in headers:
        parts = header.split(":")
        if len(parts) > 1:
            out[parts[0]] = parts[1]
    return out

def main():
    try:
        # Server on the standard webserver port of 80.
        server = HTTPServer(('', 8001), MyHandler)
        print("Starting webpage server...")
        server.serve_forever()
    except KeyboardInterrupt:
        print(' received, closing server.')
        server.socket.close()

if __name__ == '__main__':
    main()
