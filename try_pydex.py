from pydexcom import Dexcom


def try_pydex(username, password):
    dexcom = Dexcom(username=username, password=password)
    glucose_reading = dexcom.get_current_glucose_reading()
    print(glucose_reading)

def get_creds(file):
    with open(file, 'r') as f:
        contents = f.read().strip().split()
        if len(contents) != 2:
            raise ValueError("File must contain exactly two words: username and password.")
        return contents[0], contents[1]

if __name__ == "__main__":
    user, password = get_creds('.credentials.txt')
    try_pydex(user, password)
