#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from urllib.parse import parse_qsl
from binascii import hexlify
from http.cookies import SimpleCookie
from startup import DOMAIN

import magic
import os
import time
import logging
import Auth

logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel(logging.INFO)

MIME_TYPE_OVERRIDES = {
	"css": "text/css"
}

RESPONSE_OVERRIDES = {
	".ssl": 404,
	"servers.py": 404
}

COOKIES = Auth.CookieUtils.load_cookies()

ACCOUNTS = Auth.PasswordUtils.load_passwords()


class Server(BaseHTTPRequestHandler):
	LOGIN_PAGES = ("login.html", "reset.css", "login.css", "login.png")

	def __init__(self, request, client_address, server):
		self.string_to_send = ""
		self.status_code = 200
		self.mime_type = "text/html"
		self.file_extension = ""
		self.path = ""
		self.cookies = {}
		self.cookie = None
		super().__init__(request, client_address, server)  # Make sure this call is last because it is a blocking call

	# This method is to suppress annoying logging
	def log_message(self, format, *args):
		pass

	def create_and_send_response(self, code, string_to_send, mime_type, cookie=None):
		self.send_response(code)
		self.send_header('Cache-Control', 'no-store')

		if mime_type is not None:
			self.send_header('Content-type', mime_type)

		if cookie is not None:
			self.send_header('Set-Cookie', cookie)

		self.end_headers()

		if string_to_send is not None:
			self.wfile.write(string_to_send)

	def create_and_send_error(self, code):
		if self.status_code != code:
			self.path = str(code) + ".html"
			with open("web/" + self.path, 'rb') as file_to_get:
				self.string_to_send = file_to_get.read()
				self.status_code = code
			self.mime_type = "text/html"
			self.create_and_send_response(self.status_code, self.string_to_send, self.mime_type)

	def send_redirect(self, location, cookie=None):
		self.send_response(301)
		self.send_header('Cache-Control', 'no-store')
		if cookie is not None:
			self.send_header('Set-Cookie', cookie)
		self.send_header('Location', location)
		self.end_headers()

	def check_response_overrides(self):
		for directory in self.path.split("/"):
			if directory in RESPONSE_OVERRIDES:
				self.create_and_send_error(RESPONSE_OVERRIDES[directory])
				return True
		return False

	def do_GET(self):
		self.path = self.path[1:]  # Cut off to leading "/" to make the path relative

		cookie_header = SimpleCookie(self.headers["Cookie"])
		for key, morsel in cookie_header.items():
			self.cookies[key] = morsel.value
		del cookie_header

		self.cookie = list(set(self.cookies.values()).intersection(set(COOKIES)))

		# Prevent people from accessing non-login pages without a cookie
		if not self.cookie and (self.path not in Server.LOGIN_PAGES):
			self.send_redirect(f"https://{DOMAIN}/login.html")
			return

		# Update time when cookie was last accessed
		if self.cookie:
			COOKIES[self.cookie[0]] = int(time.time())  # There should only ever be one element. Two elements is bad

		# Remove bad trailing slashes
		if self.path.rfind("/") == len(self.path) - 1:  # Trust me, this is fine. I promise
			self.path = self.path[:-1]

		if self.check_response_overrides():
			return

		# Redirect an empty path to the main page
		if self.path == "":
			self.path = "index.html"

		self.status_code = 200
		self.file_extension = self.path[-(len(self.path) - 1 - self.path.rfind(".")):]  # Ugly but works
		if self.file_extension in MIME_TYPE_OVERRIDES:
			self.mime_type = MIME_TYPE_OVERRIDES[self.file_extension]
		else:
			try:
				# Set mime type
				self.mime_type = magic.from_file("web/" + self.path, mime=True)
			except IOError:
				self.create_and_send_error(404)
				return

		try:
			with open("web/" + self.path, 'rb') as file_to_get:
				self.string_to_send = file_to_get.read()
		except IOError:
			self.create_and_send_error(404)
			return

		# Send all the data!
		self.create_and_send_response(self.status_code, self.string_to_send, self.mime_type)

	def do_POST(self):
		if self.path == "/login.html":
			content_length = int(self.headers['Content-Length'])
			post_data = parse_qsl(self.rfile.read(content_length).decode("utf-8"))

			if Auth.PasswordUtils.verify_password(post_data[0][1], post_data[1][1]):
				session_id = hexlify(os.urandom(16)).decode('ascii')
				created_cookie = f"SID={session_id}; Path=/; Secure; Expires=Tue, 19 Jan 2038 04:14:07"
				COOKIES[session_id] = int(time.time())
				self.send_redirect(f'https://{DOMAIN}/', cookie=created_cookie)
			else:
				self.send_redirect(f'https://{DOMAIN}/login.html')


class RedirectServer(BaseHTTPRequestHandler):
	# This method is to suppress logging
	def log_message(self, format, *args):
		pass

	def do_GET(self):
		self.send_response(301)
		self.send_header('Cache-Control', 'no-store')
		self.send_header('Location', f'https://{DOMAIN}')
		self.end_headers()


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	"""Handle requests in a separate thread."""
