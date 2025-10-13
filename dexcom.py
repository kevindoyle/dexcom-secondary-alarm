from pydexcom import Dexcom


def get_creds(file):
    with open(file, 'r') as f:
        contents = f.read().strip().split()
        if len(contents) != 2:
            raise ValueError("File must contain exactly two words: username and password.")
        return contents[0], contents[1]

def get_glucose_number(username, password):
    user, password = get_creds('.credentials.txt')
    dexcom = Dexcom(username=username, password=password)
    glucose_reading = dexcom.get_current_glucose_reading()
    return glucose_reading.value