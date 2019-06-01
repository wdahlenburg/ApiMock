#!/bin/python

# ApiMock (@wdahlenb)

'''
    Quickly mock up a back-end API using raw HTTP request/responses. Change the results on the fly.

    Lax mode: Whatever the URL is we will give the response. HTTP verb doesn't matter.

    Strict mode: VERB + URL must match

'''

import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import ssl

ROUTES = {}
ARGS = {}

# Main method
def main():
    global ROUTES, ARGS
    # Parse Arguments
    ARGS = parse_args()

    # Set the mode
    if ARGS.mode == 'strict':
        ROUTES = generate_strict_routes(ARGS.directory)
    else:
        ROUTES = generate_lax_routes(ARGS.directory)

    # Create the server
    httpd = HTTPServer((ARGS.server, ARGS.port), SimpleHTTPRequestHandler)
    if (ARGS.tls and ARGS.keyfile and ARGS.certfile):
        httpd.socket = ssl.wrap_socket(
            httpd.socket,
            keyfile=ARGS.keyfile,
            certfile=ARGS.certfile,
            cert_reqs=ssl.CERT_NONE,
            server_side=True,
            ssl_version=ssl.PROTOCOL_TLSv1_2)
    try:
        httpd.serve_forever()
    except BaseException:
        pass

# Parse the input arguments
def parse_args():
    parser = argparse.ArgumentParser(
        description='ApiMock: Quickly mock back-end responses from local files\n')
    parser.add_argument(
        '-d',
        '--directory',
        required=True,
        help='Directory containing requests and responses',
        action=CheckDirectory)
    parser.add_argument(
        '-s',
        '--server',
        nargs='?',
        default='127.0.0.1',
        help='Host for the server to run on. Ex: 192.168.1.10')
    parser.add_argument(
        '-p',
        '--port',
        nargs='?',
        default=3000,
        help='Port for the server to listen on. Default=3000',
        type=int)
    parser.add_argument(
        '-m',
        '--mode',
        nargs='?',
        default='lax',
        help='Modes. Either strict or lax. Default lax')
    parser.add_argument(
        '-tls',
        nargs='?',
        default=False,
        help='Enforce TLS. Default false',
        type=bool)
    parser.add_argument(
        '-k',
        '--keyfile',
        nargs='?',
        default=None,
        help='Keyfile for TLS')
    parser.add_argument(
        '-c',
        '--certfile',
        nargs='?',
        default=None,
        help='Keyfile for TLS')

    return parser.parse_args()

# Ensure the proper file permissions are applied to the input directory
class CheckDirectory(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        prospective_dir = values
        if not os.path.isdir(prospective_dir):
            raise argparse.ArgumentTypeError(
                "readable_dir:{0} is not a valid path".format(prospective_dir))
        if os.access(prospective_dir, os.R_OK):
            setattr(namespace, self.dest, prospective_dir)
        else:
            raise argparse.ArgumentTypeError(
                "readable_dir:{0} is not a readable dir".format(prospective_dir))


'''
    Iterates through all of the files in the specified directory with the .req and .resp extension

    Generates a valid route for a req and response. The basename must be the same.

    test1.req matches with test1.resp
    test2.req matches with test2.resp
    etc

    * Not intended to perform recursion through folders
'''
def generate_lax_routes(directory):
    files = os.listdir(directory)
    reqs = [f for f in files if f.endswith('.req')]
    resps = [f for f in files if f.endswith('.resp')]

    routes = {}

    for req in reqs:
        name = req.split('.req')[0]
        if name + '.resp' in resps:
            _, path = get_details(directory + '/' + req)
            routes[path] = name + '.resp'

    return routes

# Ensure that the verb and path are correct
def generate_strict_routes(directory):
    files = os.listdir(directory)
    reqs = [f for f in files if f.endswith('.req')]
    resps = [f for f in files if f.endswith('.resp')]

    routes = {'GET': {}, 'POST': {}}

    for req in reqs:
        name = req.split('.req')[0]
        if name + '.resp' in resps:
            verb, path = get_details(directory + '/' + req)
            if verb.upper() == 'GET':
                routes['GET'][path] = name + '.resp'
            elif verb.upper() == 'POST':
                routes['POST'][path] = name + '.resp'

    return routes

# Get the proper url path and verb from the request file
def get_details(req_file):
    with open(req_file) as file:
        first_line = file.readline()
        split_values = first_line.split()
        return split_values[0], split_values[1]

# Get the correct status code, headers, and body from the proper response file
def get_response(resp_file):
    blacklist = ['date']
    data = {'status_code': -1, 'headers': {}, 'body': ''}
    try:
        with open(resp_file) as file:
            first_line = file.readline()
            data['status_code'] = int(first_line.split()[1])

            lines = file.readlines()
            headers_end_index = lines.index('\n')
            for line_index in range(headers_end_index):
                header_line = lines[line_index].split(':')
                key = header_line[0]
                val = header_line[1].strip()
                if key.lower() not in blacklist:
                    data['headers'][key] = val

            data['body'] = '\n'.join(lines[headers_end_index + 1:])
    except BaseException:
        pass

    return data

# Simple server to host GET and POST requests
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    BaseHTTPRequestHandler.sys_version = ''
    server_version = ''

    # Strip the server string
    def version_string(self):
        return self.server_version

    # Handle GET requests
    def do_GET(self):
        prefix = ROUTES['GET'] if ARGS.mode == 'strict' else ROUTES
        if self.path in prefix.keys():
            response = get_response(ARGS.directory + '/' + prefix[self.path])
            self.send_response(response['status_code'])
            for header in response['headers'].keys():
                if header.lower() == 'server':
                    # Ignore because python makes the Server header hard to
                    # access
                    pass
                else:
                    self.send_header(header, response['headers'][header])
            self.end_headers()
            self.wfile.write(str.encode(response['body']))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'ApiMock: Path not found')

    # Handle POST requests
    def do_POST(self):
        prefix = ROUTES['POST'] if ARGS.mode == 'strict' else ROUTES
        if self.path in prefix.keys():
            response = get_response(ARGS.directory + '/' + prefix[self.path])
            self.send_response(response['status_code'])
            for header in response['headers'].keys():
                if header.lower() == 'server':
                    # Ignore because python makes the Server header hard to
                    # access
                    pass
                else:
                    self.send_header(header, response['headers'][header])
            self.end_headers()
            self.wfile.write(str.encode(response['body']))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'ApiMock: Path not found')


if __name__ == "__main__":
    main()
