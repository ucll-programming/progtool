import asyncio
import logging
from typing import Optional
import threading


def create_background_worker() -> asyncio.AbstractEventLoop:
    def thread_proc():
        nonlocal event_loop
        logging.info('Background thread reporting for duty')
        event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(event_loop)

        event.set()

        try:
            logging.info('Background thread getting ready to process tasks')
            event_loop.run_forever()
        finally:
            event_loop.close()

    event_loop: Optional[asyncio.AbstractEventLoop] = None
    event = threading.Event()

    thread = threading.Thread(target=thread_proc, daemon=True, name="BGThread")
    thread.start()

    event.wait()
    assert event_loop is not None, 'BUG: event loop should have been created by background thread'

    return event_loop
