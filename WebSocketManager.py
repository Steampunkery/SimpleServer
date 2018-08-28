from threading import Thread
from startup import DOMAIN
from SimpleWebSocketServer import SimpleSSLWebSocketServer, WebSocket
from multiprocessing import Process, Pipe, Manager

import logging
import time
import Backend

logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel(logging.INFO)

STOP = False


def handle_clients():
	manager = Manager()
	queue = manager.Queue()

	backend_process = Process(target=Backend.run, args=(queue,))
	backend_process.start()

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
			for client in WebSocketClient.clients:
				client.sendMessage(str(data))
		if time.time() > timeout and not STOP:
			break

	backend_process.terminate()


def process_client(client):
	# Tm.MetaTransferManager.register('TransferManager', Tm.TransferManager, exposed=['add_to_queue', 'get_queue'])
	#
	# manager = Tm.MetaTransferManager()
	# manager.start()
	#
	# transfer_manager = manager.TransferManager()

	recv_pipe, send_pipe = Pipe(duplex=False)
	backend_process = Process(target=Backend.run, args=(send_pipe,))
	backend_process.start()

	# Loop with a 5 second timeout
	# TODO: Make timer configurable
	"""
	It is important to include some kind of a timeout or condition that halts the loop.
	If you don't do this, the process will never join. You could even set a boolean in
	the function that handle SIGTERM to terminate it. Just make sure that it does terminate at some point.
	"""
	timeout = time.time() + 5
	while True:
		time.sleep(0.5)
		if recv_pipe.poll():
			timeout = time.time() + 5
			data = recv_pipe.recv()
			client.sendMessage(str(data))
		if time.time() > timeout and not STOP:
			break

	backend_process.join()


class WebSocketClient(WebSocket):

	clients = []
	total_clients = 0

	def __init__(self, server, sock, address):
		super().__init__(server, sock, address)
		self.id = None

	def handleConnected(self):
		# TODO: Make this if statement configurable
		if False:
			Thread(target=process_client, args=(self,), daemon=True).start()
		else:
			WebSocketClient.clients.append(self)
		self.id = WebSocketClient.total_clients
		logger.info(f"Client {self.id} has connected")
		WebSocketClient.total_clients += 1

	def handleClose(self):
		logger.info(f"Client {self.id} has disconnected")
		WebSocketClient.clients.remove(self)


def run(port=8000):
	server = SimpleSSLWebSocketServer(DOMAIN, port, WebSocketClient, ".ssl/site.crt", ".ssl/site.key")
	Thread(target=server.serveforever, daemon=True).start()
	logger.info(f"Listening for WebSocket connections on {port}...")

	# TODO: Make this if configurable
	if True:
		handle_clients()
