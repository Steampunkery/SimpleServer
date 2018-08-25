from threading import Thread
from startup import DOMAIN
from SimpleWebSocketServer import SimpleSSLWebSocketServer, WebSocket

import logging
import time

logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel(logging.INFO)


def handle_clients(transfer_manager):
	while True:
		time.sleep(1)
		if transfer_manager.transferQueue:
			data = transfer_manager.transferQueue.popleft()
			for client in WebSocketClient.clients:
				client.sendMessage(str(data))
				print("test")


class WebSocketClient(WebSocket):

	clients = []
	total_clients = 0

	def __init__(self, server, sock, address):
		super().__init__(server, sock, address)
		self.id = None

	def handleConnected(self):
		WebSocketClient.clients.append(self)
		self.id = WebSocketClient.total_clients
		logger.info(f"Client {self.id} has connected")
		WebSocketClient.total_clients += 1

	def handleClose(self):
		logger.info(f"Client {self.id} has disconnected")
		WebSocketClient.clients.remove(self)


def run(transfer_manager, port=8000):
	server = SimpleSSLWebSocketServer(DOMAIN, port, WebSocketClient, ".ssl/site.crt", ".ssl/site.key")
	Thread(target=server.serveforever, daemon=True).start()
	logger.info(f"Listening for WebSocket connections on {port}...")

	handle_clients(transfer_manager)
