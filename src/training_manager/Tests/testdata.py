import json
import Tests.passwords

good_username = "good_username"
bad_username = "bad_username"
good_modelname = "good_modelname"
bad_modelname = "bad_modelname"

smip_auth = {
  "authenticator": "maxdemo",
  "password": "{smip_password}".format(smip_password=Tests.passwords.smip_password),
  "username": "maxdemo",
  "role": "rpi_ro_group",
  "url": "https://rpi.cesmii.net/graphql",
}

attribute1 = {
  "attrib_id": "27084",
  "displayName": "Temperature - Equipment",
  "dataType": "FLOAT",
  "start_time": "2019-01-02:00:00.000+00:00",
  "end_time":   "2019-01-08:00:00.000+00:00",
  "max_samples": 0,
  "result": b'ts,27084\n2019-01-02 00:00:00+00:00,10.0\n2019-01-03 00:00:00+00:00,20.0\n2019-01-04 00:00:00+00:00,30.0\n2019-01-05 00:00:00+00:00,40.0\n2019-01-06 00:00:00+00:00,50.0\n2019-01-07 00:00:00+00:00,60.0\n2019-01-08 00:00:00+00:00,\n'
}

attribute2 = {
  "attrib_id": "27077",
  "displayName": "Flow Rate - Mass- In",
  "dataType": "FLOAT",
  "start_time": "2019-01-02:00:00.000+00:00",
  "end_time":   "2019-01-09:00:00.000+00:00",
  "max_samples": 0,
}

trainer_str = ""

