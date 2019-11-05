import sys
import time
import Adafruit_DHT
import paho.mqtt.client as mqtt
import json
import os

# initial
sensor = Adafruit_DHT.DHT22
pin = 3

NEXPIE_HOST = "jupiter.scg.com"
CLIENT_ID = ""
DEVICE_TOKEN = ""

sensor_data = {'temperature': 0, 'humidity': 0}

def on_connect(client, userdata, flags, rc):
    print("Result from connect: {}".format(
        mqtt.connack_string(rc)))
    client.subscribe("@msg/test")


def on_subscribe(client, userdata, mid, granted_qos):
    print("I've subscribed")


def on_message(client, userdata, msg):
    print("Message received. Topic: {}. Payload: {}".format(
        msg.topic, str(msg.payload)))


client = mqtt.Client(protocol=mqtt.MQTTv311,
                     client_id=CLIENT_ID, clean_session=True)
client.username_pw_set(DEVICE_TOKEN)
client.on_connect = on_connect
client.on_subscribe = on_subscribe
client.on_message = on_message
client.connect(NEXPIE_HOST, 1883)
client.loop_start()

try:
    while True:
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

        if humidity is not None and temperature is not None:
            humidity = round(humidity, 2)
            temperature = round(temperature, 2)
            print(u"Temperature: {:g}\u00b0C, Humidity: {:g}%".format(temperature, humidity))
            sensor_data['temperature'] = temperature
            sensor_data['humidity'] = humidity
            print(json.dumps({"data": sensor_data}))
            client.publish('@shadow/data/update', json.dumps({"data": sensor_data}), 1)
            time.sleep(2)
        else:
            print('Failed to get reading. Try again!')
except KeyboardInterrupt:
    pass

client.loop_start()
client.disconnect()
