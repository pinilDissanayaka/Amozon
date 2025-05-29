import random
import time

def random_sleep(min_time=1, max_time=3):
    time.sleep(random.uniform(min_time, max_time))