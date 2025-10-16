from pydexcom import Dexcom
import asyncio

class DexcomClient():
    def __init__(self, creds_file):
        username, password = get_creds(creds_file)
        self.username = username
        self.password = password
        self.client = Dexcom(username=username, password=password)
        self.result_queue = asyncio.Queue()

    def get_glucose_number(self):
        glucose_reading = self.client.get_current_glucose_reading()
        return glucose_reading.value

    def get_result_queue(self):
        return self.result_queue

    def update_interval(self):
        return 5*60


def get_creds(file):
    with open(file, 'r') as f:
        contents = f.read().strip().split()
        if len(contents) != 2:
            raise ValueError("File must contain exactly two words: username and password.")
        return contents[0], contents[1]

def get_glucose_number():
    username, password = get_creds('.credentials.txt')
    dexcom = Dexcom(username=username, password=password)
    glucose_reading = dexcom.get_current_glucose_reading()
    return glucose_reading.value

def get_update_interval_seconds():
    return 5*60