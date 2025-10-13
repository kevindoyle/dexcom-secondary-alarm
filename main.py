import time
from dexcom import get_glucose_number as get_dexcom_bg
import asyncio # TODO: read https://docs.python.org/3/howto/a-conceptual-overview-of-asyncio.html#a-conceptual-overview-of-asyncio


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


async def start_system():
    bg_queue = asyncio.Queue()

    async def polling():
        bg = get_dexcom_bg()
        await bg_queue.put(bg)

    should_stop = False
    def stopper():
            #TODO: put this onto a queue?
            return not should_stop

    async def poll_timer():
        print("poll timer sleep for 12 minutes")
        await asyncio.sleep(12*60)
        print("Stopping polling")
        should_stop = True   
    
    print("Starting do_polling")
    poller = asyncio.create_task(do_polling(stopper, polling, 5*60))
    timer = asyncio.create_task(poll_timer())

    while stopper():
        try:
            bg = bg_queue.get_nowait()
            print(f"bg from queue: {bg}")
        except asyncio.QueueEmpty:
            await asyncio.sleep(1)
            continue
        finally:
            poller.cancel()
            await gather(poller, return_exceptions=True)
            print("polling complete")

    try:
        timer.cancel()
        await gather(timer, return_exceptions=True)
    except Exception as e:
        print(f"Exception when cancelling timer: {e}")

    try:
        poller.cancel()
        await gather(poller, return_exceptions=True)
    except Exception as e:
        print(f"Exception when cancelling poller (maybe the second time): {e}")
    
    print("end of start_system")

if __name__ == "__main__":
    start_system()
    print("end of main")
