import time
import random


def generate_unique_name(name: str = 'Figure'):
    timestamp = int(time.time())
    random_number = random.randint(1000, 9999)
    return f"{name}_{timestamp}_{random_number}"
