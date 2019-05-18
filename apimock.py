#!/bin/python

# ApiMock (@wdahlenb)

'''
	Lax mode: Whatever the URL is we will give the response. HTTP verb doesn't matter.

	Strict mode: VERB + URL must match

'''

import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import os

import pdb

class check_directory(argparse.Action):
	def __call__(self, parser, namespace, values, option_string=None):
		prospective_dir=values
		if not os.path.isdir(prospective_dir):
			raise argparse.ArgumentTypeError("readable_dir:{0} is not a valid path".format(prospective_dir))
		if os.access(prospective_dir, os.R_OK):
			setattr(namespace,self.dest,prospective_dir)
		else:
			raise argparse.ArgumentTypeError("readable_dir:{0} is not a readable dir".format(prospective_dir))

parser = argparse.ArgumentParser(description='ApiMock: Quickly mock back-end responses from local files\n')
parser.add_argument('-d', '--directory', required=True, help='Directory containing requests and responses', action=check_directory)
parser.add_argument('-s', '--server', nargs='?', default='127.0.0.1', help='Host for the server to run on. Ex: 192.168.1.10')
parser.add_argument('-p', '--port', nargs='?', default=3000, help='Port for the server to listen on. Default=3000')
parser.add_argument('-m', '--mode', nargs='?', default='lax', help='Modes. Either strict or lax. Default lax')

args = parser.parse_args()

'''
	Iterates through all of the files in the specified directory with the .req and .resp extension

	Generates a valid route for a req and response. The basename must be the same.

	test1.req matches with test1.resp
	test2.req matches with test2.resp
	etc

	* Not intended to perform recursion through folders

'''
def generateLaxRoutes(directory):
	files = os.listdir(directory)
	reqs = [f for f in files if f.endswith('.req')]
	resps = [f for f in files if f.endswith('.resp')]

	routes = {}

	for req in reqs:
		name = req.split('.req')[0]
		if name + '.resp' in resps:
			path = getPath(directory + '/' + req)
			routes[path] = name + '.resp'

	return routes


def getPath(request):
	with open(request) as f:
		first_line = f.readline()
		return first_line.split()[1]

def getResponse(respFile):
	blacklist = ['date']
	data = {'code': -1, 'headers': {}, 'body': ''}
	try:
		with open(respFile) as f:
			first_line = f.readline()
			data['code'] = int(first_line.split()[1])

			lines = f.readlines()
			headersRange = lines.index('\n')
			for lineIndex in range(headersRange):
				splitArr = lines[lineIndex].split(':')
				key = splitArr[0]
				val = splitArr[1].strip()
				if key.lower() not in blacklist:
					data['headers'][key] = val

			data['body'] = '\n'.join(lines[headersRange + 1:])
	except:
		pass

	return data

routes = generateLaxRoutes(args.directory)

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

	BaseHTTPRequestHandler.sys_version = ''
	server_version = ''

	def version_string(self):
		return self.server_version

	def do_GET(self):
		if self.path in routes.keys():
			response = getResponse(args.directory + '/' + routes[self.path])
			self.send_response(response['code'])
			for header in response['headers'].keys():
				if header.lower() == 'server':
					# Ignore because python is stupid
					pass
				else:
					self.send_header(header, response['headers'][header])
			self.end_headers()
			self.wfile.write(str.encode(response['body']))
		else:
			self.send_response(404)
			self.end_headers()
			self.wfile.write(b'ApiMock: Path not found')

	def do_POST(self):
		if self.path in routes.keys():
			response = getResponse(args.directory + '/' + routes[self.path])
			self.send_response(response['code'])
			for header in response['headers'].keys():
				if header.lower() == 'server':
					# Ignore because python is stupid
					pass
				else:
					self.send_header(header, response['headers'][header])
			self.end_headers()
			self.wfile.write(str.encode(response['body']))
		else:
			self.send_response(404)
			self.end_headers()
			self.wfile.write(b'ApiMock: Path not found')

httpd = HTTPServer((args.server, args.port), SimpleHTTPRequestHandler)
httpd.serve_forever()