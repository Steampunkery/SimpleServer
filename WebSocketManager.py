from threading import Thread
from startup import DOMAIN
from SimpleWebSocketServer import SimpleSSLWebSocketServer, WebSocket
from multiprocessing import Process, Pipe, Manager

import logging
import time
import Backend
import json

logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel(logging.INFO)

# TODO: Move this to the README
"""
Format of a JSON packet:
{
	"css_selector": "div",
	"payload": "lorem ipsum dolor sit amet",
	"overwrite": "true"
}

css_selector: A valid css selector used to determine which element's content to change
payload: The text to deliver to the page. Could be plaintext, or it could be more HTML
overwrite: Whether the new content should overwrite the old content or replace it (default is true)
"""


def create_json(css_selector, payload, overwrite=True):
	return json.dumps(
		{
			"css_selector": css_selector,
			"payload": str(payload),
			"overwrite": str(overwrite).lower()
		}
	)


def handle_clients():
	manager = Manager()
	queue = manager.Queue()

	WebSocketHandler.processes.append(Process(target=Backend.run, args=(queue,)))
	WebSocketHandler.processes[-1].start()

	"""
	The concept here is this loop receives a random number from Backend.run every second.
	If there's no number for 5 seconds, clearly something is wrong, so break the loop and terminate the process.
	"""
	timeout = time.time() + 5
	while True:
		time.sleep(1)
		if not queue.empty():
			timeout = time.time() + 5
			data = queue.get_nowait()
			for client in WebSocketHandler.clients:
				client.sendMessage(create_json("div", data))
		if time.time() > timeout or WebSocketHandler.stop:
			break

	"""
	Manually terminate the process here because something probably went wrong,
	like the backend being stopped by and outside program
	"""
	WebSocketHandler.processes[-1].terminate()


def process_client(client):
	recv_pipe, send_pipe = Pipe(duplex=False)
	backend_process = Process(target=Backend.run, args=(send_pipe,))
	backend_process.start()

	# Loop with a 5 second timeout
	# TODO: Make timer configurable
	"""
	It is important to include some kind of a timeout or condition that halts the loop.
	If you don't do this, the process will never join. You could even set a boolean in
	the function that handle SIGTERM to terminate it (current impl). Just make sure that it does terminate at some point.
	"""
	timeout = time.time() + 5
	while True:
		time.sleep(0.5)
		if recv_pipe.poll():
			timeout = time.time() + 5
			data = recv_pipe.recv()
			client.sendMessage(create_json("div", data, overwrite=True))
		if time.time() > timeout or WebSocketHandler.stop:
			break

	backend_process.join()


class WebSocketHandler(WebSocket):

	clients = []
	processes = []
	total_clients = 0
	stop = False

	def __init__(self, server, sock, address):
		super().__init__(server, sock, address)
		self.id = None

	def handleConnected(self):
		# TODO: Make this if statement configurable
		if False:
			Thread(target=process_client, args=(self,), daemon=True).start()
		else:
			WebSocketHandler.clients.append(self)
		self.id = WebSocketHandler.total_clients
		logger.info(f"Client {self.id} has connected")
		WebSocketHandler.total_clients += 1

	def handleClose(self):
		logger.info(f"Client {self.id} has disconnected")
		WebSocketHandler.clients.remove(self)

	@classmethod
	def cleanup(cls):
		cls.stop = True


def run(port=8000):
	server = SimpleSSLWebSocketServer(DOMAIN, port, WebSocketHandler, ".ssl/site.crt", ".ssl/site.key")
	Thread(target=server.serveforever, daemon=True).start()
	logger.info(f"Listening for WebSocket connections on {port}...")

	# TODO: Make this if configurable
	if True:
		handle_clients()
