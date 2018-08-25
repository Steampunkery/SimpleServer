#!/usr/bin/python3
import logging
import signal
import sys
import ssl

import WebSocketManager
import TransferManager
import Backend
import Auth

from ThreadPool import Pool
from web.servers import Server, RedirectServer, ThreadedHTTPServer


logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel(logging.INFO)

context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
context.load_cert_chain(".ssl/site.pem")
context.set_ciphers("ALL:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!3DES:!MD5:!PSK")

DOMAIN = "localhost"


def main(server_class=ThreadedHTTPServer, handler_class=Server, port=443):
	# Closure to gracefully handle ^C
	# noinspection PyUnusedLocal
	def signal_handler(signal_, frame):
		exit_code = 0

		https.server_close()
		print()
		logger.info('Stopping https...')

		logger.info('Writing cookies...')
		try:
			Auth.CookieUtils.store_cookies()
		except IOError:
			logger.error("File cookies.json could not be opened for writing, new clients will need to re-authenticate.")
			exit_code = 1

		logger.info('Writing passwords...')
		try:
			Auth.PasswordUtils.store_passwords()
		except IOError:
			logger.error("Passwords could not be written. THIS IS BAD. Check passwd file, please!")
			exit_code = 1

		sys.exit(exit_code)

	signal.signal(signal.SIGINT, signal_handler)

	https = server_class(("0.0.0.0", port), handler_class)
	https.socket = context.wrap_socket(https.socket, server_side=True)
	logger.info(f'Starting https on port {port}...')

	https.serve_forever()


def start_http(server_class=ThreadedHTTPServer, handler_class=RedirectServer, port=80):
	httpd = server_class(("0.0.0.0", port), handler_class)
	logger.info(f'Starting httpd on port {port}...')

	httpd.serve_forever()


if __name__ == "__main__":
	transfer_manager = TransferManager.TransferManager()

	threadPool = Pool(5)

	# Add each function as a task that runs in a thread to prevent blocking the main thread
	threadPool.add_task(Backend.run, transfer_manager)
	threadPool.add_task(WebSocketManager.run, transfer_manager)
	threadPool.add_task(start_http)
	threadPool.add_task(Auth.CookieUtils.cookie_check_timer)
	threadPool.add_task(Auth.CookieUtils.cookie_write_timer)

	if len(sys.argv) == 2:
		main(port=int(sys.argv[1]))
	else:
		main()
