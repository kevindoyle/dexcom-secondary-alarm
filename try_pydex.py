from pydexcom import Dexcom
import time


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

def monitor_glucose(username, password):
    """
    Calls try_pydex as described:
    1. Call once and get a number.
    2. Call once a minute until a different number is returned.
    3. Wait 4 minutes, call again, expect the same number.
    4. Call every 20 seconds until a new number is returned.
    5. Call every 5 minutes thereafter.
    """
    def get_number():
        dexcom = Dexcom(username=username, password=password)
        reading = dexcom.get_current_glucose_reading()
        return reading.value

    print("Initial call...")
    last_number = get_number()
    print(f"Initial number: {last_number}")

    # Step 2: Call once a minute until a different number is returned
    while True:
        time.sleep(60)
        current_number = get_number()
        print(f"Minute check: {current_number}")
        if current_number != last_number:
            print("Number changed!")
            break
    # Step 3: Wait 4 minutes, call again, expect the same number
    print("Waiting 4 minutes...")
    time.sleep(4 * 60)
    check_number = get_number()
    print(f"4-min check: {check_number}")
    if check_number != current_number:
        print("Warning: Number changed unexpectedly after 4 minutes.")
    # Step 4: Call every 20 seconds until a new number is returned
    print("Polling every 20 seconds for a new number...")
    while True:
        time.sleep(20)
        new_number = get_number()
        print(f"20-sec check: {new_number}")
        if new_number != check_number:
            print("New number detected!")
            break
    # Step 5: Call every 5 minutes
    print("Switching to 5-minute polling...")
    while True:
        time.sleep(5 * 60)
        polled_number = get_number()
        print(f"5-min check: {polled_number}")
        if polled_number != new_number:
            print("Number changed again!")
            new_number = polled_number

if __name__ == "__main__":
    user, password = get_creds('.credentials.txt')
    monitor_glucose(user, password)
