from typing import Iterable
import requests

class SamplerRequestManager:
    def __init__(self, url: str, mko: str):
        self.url = url
        self.mko = mko

    def get_sample(self, data: Iterable, samples: int):
        params = {
            "x": data,
            "samples": samples
        }

        resp = requests.get(self.url, params=params)
        
        if resp.status_code != 200:
            # throw error
            pass

        

            
    

