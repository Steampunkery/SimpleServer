import collections


class TransferManager():
	def __init__(self):
		self.transferQueue = collections.deque()

	def add_to_queue(self, message):
		# If the message is an iterable but not a string, add each item
		if isinstance(message, collections.Iterable) and type(message) != str:
			self.transferQueue.extend(message)
			return
		# Else just add the message
		self.transferQueue.append(message)
