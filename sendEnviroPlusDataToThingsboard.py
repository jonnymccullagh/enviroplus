#!/usr/bin/env python

import json
import requests
from bme280 import BME280

# imports for weather sensor
try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus

# imports for light sensor
try:
    # Transitional fix for breaking change in LTR559
    from ltr559 import LTR559
    ltr559 = LTR559()
except ImportError:
    import ltr559

# gas sensor
from enviroplus import gas

# particulates
from pms5003 import PMS5003, ReadTimeoutError

import logging

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

THINGSBOARD_HOST = "http://changeme:8080"
ACCESS_TOKEN = "changeme"

bus = SMBus(1)
bme280 = BME280(i2c_dev=bus)

temperature = bme280.get_temperature()
pressure = bme280.get_pressure()
humidity = bme280.get_humidity()

lux = ltr559.get_lux()
prox = ltr559.get_proximity()

gas_readings = gas.read_all()

oxidising = gas.read_oxidising()
reducing = gas.read_reducing()
nh3 = gas.read_nh3()
adc = gas.read_adc()

pms5003 = PMS5003()
try:
    particulates = pms5003.read()
except ReadTimeoutError:
    pms5003 = PMS5003()

data_dict = {
    "temperature": temperature,
    "pressure": pressure,
    "humidity": humidity,
    "lux": lux,
    "prox": prox,
    "oxidising": oxidising,
    "reducing": reducing,
    "nh3": nh3,
}

LINES = iter(str(particulates).splitlines())
for LINE in LINES:

    parts = LINE.split(":")
    if parts[0] == "":
        print("not using empty line")
    else:
        data_dict[parts[0]] = str(parts[1]).replace(" ", "")

print(data_dict)
data_json = json.dumps(data_dict)


headers = {'Content-Type': 'application/json'}
payload = {'title': 'value1', 'name': 'value2'}

r = requests.post(THINGSBOARD_HOST + "/api/v1/" + ACCESS_TOKEN + "/telemetry",
                  data=data_json, headers=headers)
print("Response was %s %s " % (r.status_code, r.ok))
