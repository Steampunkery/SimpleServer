import random


def run(transfer_manager):
    while True:
        if not transfer_manager.transferQueue:
            transfer_manager.add_to_queue(random.randint(1, 1001))