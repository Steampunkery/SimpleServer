from urllib.request import urlopen
import random
import time


def run(pipe_or_queue):
	"""
	The basic idea here is this function is a representation of your backend.
	Your backend produces data, and it is sent through here to the websocket.
	Your backend should be significantly more complex, this is just a demo.
	"""
	if False:
		# If we get in here, our object should be a pipe because we're dealing with each client separately
		data = ["Hello, ", "this ", "server's ", "IP ", "is ", urlopen('http://ip.42.pl/raw').read().decode("utf-8")]
		for i in data:
			pipe_or_queue.send(i)
	else:
		"""
		It was a judgement call whether to use Queue here or not. If this block is executed, pipe_or_queue is a Queue.
		The reason for this is it's likely that when you expand upon this implementation, you'll have multiple readers
		and writers, therefore you should use a Queue. I also just wanted to show an example for posterity.
		"""
		while True:
			if pipe_or_queue.empty():
				time.sleep(1)
				pipe_or_queue.put(f"Your random number is {random.randint(0, 1000)}")
