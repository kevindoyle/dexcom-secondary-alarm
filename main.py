import time
from collections import deque
import asyncio # https://docs.python.org/3/howto/a-conceptual-overview-of-asyncio.html#a-conceptual-overview-of-asyncio

from alert import decide_alert
from dexcom import DexcomClient

async def do_polling(stop_fn, poll_fn, update_interval):
    """
    Calls poll_fn() every update_interval seconds, within 20 seconds of the update time.
    Stops when stop_fn returns False.

    Note: Depends on updates from fn() to be variable. Will not work if fn() returns the same value multiple times.
    """

    # Sync polling with update interval.
    poll_time = update_interval
    init_val = await poll_fn()
    # We will refine the period of updates to within 20 seconds 
    while poll_time > 20:

        if poll_time < update_interval:
            # We know the value just updated within poll_time of this moment,
            # so we can save API calls and sleep until we're within poll_time
            # of the next update. Then we'll poll again within that subunit
            # of time to hone in on the update interval's period.
            sleep_time = update_interval - poll_time
            print(f"do_polling: sleeping for {sleep_time} seconds (until refinement period)")
            await asyncio.sleep(update_interval-poll_time)

        poll_time = poll_time/5
        print(f"do_polling: poll_time: {poll_time}")

        # Call the fn until the returned value is different
        update_val = init_val
        # print(f"init_val: {init_val}, {type(init_val)}")
        while init_val == update_val:
            await asyncio.sleep(poll_time)
            update_val = await poll_fn()
            print(f"do_polling: {update_val} mg/dL")
            # print(f"update_val: {update_val}")
            # print(f"init_val == update_val: {init_val==update_val}, {init_val}, {type(init_val)}, {update_val}, {type(update_val)}")
        init_val = update_val


    print("do_polling: Starting regular interval polling")
    # Run until stopped
    while stop_fn():
        await asyncio.sleep(update_interval)
        bg = await poll_fn()
        print(f"do_polling: {bg} mg/dL")

    print("do_polling: Stopped polling")


async def main_routine(cgm_client):
    print("system_start: begin!")
    bg_queue = cgm_client.get_result_queue()

    async def polling():
        print("polling: making api call")
        bg = cgm_client.get_glucose_number()
        await bg_queue.put(bg)
        return bg

    ctrl = {"continue": True}
    def stopper():
        #TODO: use a queue? for consistency and refactorability
        return ctrl["continue"]

    async def poll_timer():
        run_time=26*60
        print(f"poll timer: let run for {run_time/60} minutes")
        await asyncio.sleep(run_time)
        print("poll_timer: time is up, setting 'continue' to False")
        ctrl["continue"] = False
    
    print("main_routine: Starting coroutines")
    poll_task = do_polling(stopper, polling, cgm_client.update_interval())
    poller = asyncio.create_task(poll_task)
    timer_task = poll_timer()
    timer = asyncio.create_task(timer_task)

    alert_queue = deque([100,100],maxlen=2)
    while stopper():
        try:
            bg = bg_queue.get_nowait()
            print(f"main_routine: bg from queue {bg} mg/dL")
            alert_queue.append(bg)
            do_alert = decide_alert(alert_queue)
            if do_alert:
                print(f"main_routine: !!!!!!!!!")
        except asyncio.QueueEmpty:
            await asyncio.sleep(3)
            continue

    try:
        timer.cancel()
        await asyncio.gather(timer, return_exceptions=True)
    except Exception as e:
        print(f"main_routine: Exception when cancelling timer: {e}")

    try:
        poller.cancel()
        await asyncio.gather(poller, return_exceptions=True)
    except Exception as e:
        print(f"main_routine: Exception when cancelling poller (maybe the second time): {e}")
    
    print("main_routine: end")

if __name__ == "__main__":
    cgm_client = DexcomClient('.credentials.txt')
    asyncio.run(main_routine(cgm_client))
    print("main: end")
