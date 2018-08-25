from urllib.request import urlopen


def run(transfer_manager):
        """
        Add your code here to send to the transfer queue. Or don't, it's your project.
        The below example adds "Hello, World!" to the queue when the queue is empty:

        while True:
            if not transfer_manager.transferQueue:
                transfer_manager.add_to_queue("Hello, World!")
            
        The basic idea here is you constantly add things to the queue to be sent over the websocket
        
        See TransferManager.py, WebSocketManager.py and script.js for the full setup
        """

        transfer_manager.add_to_queue(["Hello, ", "your ", "IP ", "is ", urlopen('http://ip.42.pl/raw').read().decode("utf-8")])
        print(transfer_manager.transferQueue)
