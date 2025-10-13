from pydexcom import Dexcom
import time
import asyncio # TODO: read https://docs.python.org/3/howto/a-conceptual-overview-of-asyncio.html#a-conceptual-overview-of-asyncio


def get_glucose_number(username, password):
    dexcom = Dexcom(username=username, password=password)
    glucose_reading = dexcom.get_current_glucose_reading()
    return glucose_reading.value

def get_creds(file):
    with open(file, 'r') as f:
        contents = f.read().strip().split()
        if len(contents) != 2:
            raise ValueError("File must contain exactly two words: username and password.")
        return contents[0], contents[1]

def start_system(username, password):
    def polling():
        # TODO: feed values to a processing function
        # TODO: make start_system accept a function to call here, don't hardcode the glucose call
        return get_glucose_number(username, password)

    ctrl = {"continue": True}
    def stopper():
        return ctrl["continue"]
    
    print("Starting do_polling")
    asyncio.run(do_polling(stopper, polling, 5*60))

    print("System sleep for 12 minutes")
    sleep(12*60)

    print("Stopping polling")
    ctrl["continue"] = False
    sleep(6*60)
    print("The polling should have stopped")

async def do_polling(stop_fn, poll_fn, update_interval):
    """
    Calls poll_fn() every update_interval seconds, within 20 seconds of the update time.
    Stops when stop_fn returns False.

    Note: Depends on updates from fn() to be variable. Will not work if fn() returns the same value multiple times.
    """

    # Sync polling with update interval.
    poll_time = update_interval
    init_val = poll_fn()
    # We will refine the period of updates to within 20 seconds 
    while poll_time > 20:

        if poll_time < update_interval:
            # We know the value just updated within poll_time of this moment,
            # so we can save API calls and sleep until we're within poll_time
            # of the next update. Then we'll poll again within that subunit
            # of time to hone in on the update interval's period.
            print("sleeping until it's time to start polling again")
            await asyncio.sleep(update_interval-poll_time)

        poll_time = poll_time/5
        print(f"poll_time: {poll_time}")

        # Call the fn until the returned value is different
        update_val = init_val
        print(f"init_val: {init_val}")
        while init_val == update_val:
            await asyncio.sleep(poll_time)
            update_val = poll_fn()
            print(f"update_val: {update_val}")
            print(f"init_val == update_val: {init_val==update_val}, {init_val}, {update_val}")
        init_val = update_val


    print("Starting regular interval polling")
    # Run until stopped
    while stop_fn():
        await asyncio.sleep(update_interval)
        bg = poll_fn()
        print(f"glucose: {bg}")

    print("!! Stopped polling")

if __name__ == "__main__":
    user, password = get_creds('.credentials.txt')
    start_system(user, password)
