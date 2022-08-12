import json

json_from_trainer = {
    "auth_json" : {"authenticator": "kaushp",
                "password": "welcome001",
                "name": "kaushp",
                "role": "rpi_ro_group",
                "url": "https://rpi.cesmii.net/graphql"
                },
   "query_json" : {"tag_ids": ["984"],
                "start_time": "2020-01-23T20:51:40.071032+00:00",
                "end_time": "now",
                "GMT_prefix_sign":"plus",
                "max_samples": 0,
                "Attribute": "Electric Potential",
                "Equipment": "Motor"
                 }
}

trainer_str = json.dumps(json_from_trainer)