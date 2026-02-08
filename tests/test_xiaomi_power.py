import os
import sys
import time
import logging
import asyncio

logging.basicConfig(level=logging.INFO)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from app.devices.xiaomi_cuco_switch import XiaomiCucoSwitch

async def test_cmd():
    device = XiaomiCucoSwitch()
    await device.turn_on()
    await asyncio.sleep(5)
    await device.turn_off()

    
if __name__ == '__main__':
    asyncio.run(test_cmd())