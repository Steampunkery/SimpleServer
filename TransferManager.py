from collections import deque


class TransferManager():
	def __init__(self):
		self.transferQueue = deque(maxlen=10)

	def add_to_queue(self, num):
		self.transferQueue.append(num)
