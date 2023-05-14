import asyncio

def sleep(delay: float):
    return asyncio.sleep(delay)

def get_event_loop():
    return asyncio.get_event_loop()

def create_task(coro):
    return asyncio.create_task(coro)

def run(coro):
    return asyncio.run(coro)

def start_server(callback, host, port):
    return asyncio.start_server(callback, host, port)

def new_event_loop():
    return asyncio.new_event_loop()
