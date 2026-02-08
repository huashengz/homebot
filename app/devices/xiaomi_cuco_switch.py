import logging
import requests
from app.devices.base import BaseDevice

logger = logging.getLogger(__name__)

class XiaomiCucoSwitch(BaseDevice):

    device_id = "switch.cuco_v3_8679_switch"

    def get_device_id(self):
        return self.device_id

    async def turn_on(self) -> bool:
        url = f"{self.endpoint}/api/services/switch/turn_on"
        payload = {
            "entity_id": self.device_id
        }
        logger.info(f"turn on: {self.device_id}")
        resp = requests.post(url, headers=self.get_headers(), json=payload)
        print(resp.content)
        return True

    async def turn_off(self) -> bool:
        url = f"{self.endpoint}/api/services/switch/turn_off"
        payload = {
            "entity_id": self.device_id
        }
        logger.info(f"turn off: {self.device_id}")
        requests.post(url, headers=self.get_headers(), json=payload)
        return True

