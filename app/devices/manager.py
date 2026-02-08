from typing import Dict
from app.devices.base import BaseDevice
from app.schemas import DeviceEvent


class DeviceManager:
    
    def __init__(self):
        self.devices: Dict[str, BaseDevice] = {}

    def register(self, device: BaseDevice):
        self.devices[device.get_device_id()] = device

    def notify(self, event: DeviceEvent):
        pass