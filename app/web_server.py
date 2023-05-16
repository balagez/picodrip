import machine
import uasyncio
import ntptime
import utime
import app.scheduler
import app.wlan
from app.routes import router
from app.events import Logger

led = machine.Pin("LED", machine.Pin.OUT)
log = Logger('main')

async def main():
    app.scheduler.start()
    app.wlan.connect()
    ntptime.settime()
    loop = uasyncio.get_event_loop()
    loop.set_exception_handler(handle_exception)
    loop.create_task(uasyncio.start_server(router.handle, "0.0.0.0", 80))
    while True:
        led.on()
        app.wlan.ensure_connected()
        await uasyncio.sleep(0.25)
        led.off()
        await uasyncio.sleep(5)

def handle_exception(loop, context):
    msg = context.get('exception', context['message'])
    log.error(f'Uncaught exception: {msg}')

try:
    uasyncio.run(main())
except KeyboardInterrupt:
    machine.reset()
except Exception as e:
    log.error(f'Main event loop stopped because of exception: {e}')
finally:
    uasyncio.new_event_loop()
