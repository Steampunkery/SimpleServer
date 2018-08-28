#!/usr/bin/python3
# TODO: Fix thread that sometimes doesn't join at program end
import logging
import signal
import sys
import ssl
import time

import WebSocketManager
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


def main(port=443, httpd_port=80):
	# Closure to gracefully handle ^C
	# noinspection PyUnusedLocal
	def signal_handler(signal_, frame):
		exit_code = 0

		WebSocketManager.STOP = True
		time.sleep(0.1)  # Wait for the processes to stop

		https.server_close()
		httpd.server_close()
		print()
		logger.info('Stopping http servers...')

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

	https = ThreadedHTTPServer(("0.0.0.0", port), Server)
	https.socket = context.wrap_socket(https.socket, server_side=True)
	logger.info(f'Starting https on port {port}...')

	httpd = ThreadedHTTPServer(("0.0.0.0", httpd_port), RedirectServer)
	logger.info(f'Starting httpd on port {httpd_port}...')

	# TODO: Process-ize things
	thread_pool = Pool(4)

	# Add each function as a task that runs in a thread to prevent blocking the main thread
	thread_pool.add_task(WebSocketManager.run)
	thread_pool.add_task(httpd.serve_forever)
	thread_pool.add_task(Auth.CookieUtils.cookie_check_timer)
	thread_pool.add_task(Auth.CookieUtils.cookie_write_timer)

	https.serve_forever()


if __name__ == "__main__":
	if len(sys.argv) == 2:
		main(port=int(sys.argv[1]))
	else:
		main()
