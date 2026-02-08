from app.config.settings import settings

class BaseDevice:
    
    def __init__(self):
        self.endpoint = settings.HOMEASSISTANT_ENDPOINT
        self.token = settings.HOMEASSISTANT_TOKEN

    def get_headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }

    def get_device_id(self):
        raise NotImplementedError

