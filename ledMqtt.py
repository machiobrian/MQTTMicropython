import network
import time 
import machine 
import ssl 
import ubinascii

from machine import Pin, Timer
import ntptime 
from simple import MQTTClient

SSID = "_braen"
PASS = "123567890"

MQTT_CLIENT_KEY ="private.pem.key"
MQTT_CLIENT_CERT = "certificate.pem.crt"
MQTT_BROKER = "a7tk9sth503zl-ats.iot.us-east-1.amazonaws.com"
MQTT_CLIENT_ID = ubinascii.hexlify(machine.unique_id())
MQTT_BROKER_CA = "AmazonRootCA1.pem"

# MQTT topic constants
MQTT_LED_TOPIC = "picow/led"
MQTT_BUTTON_TOPIC = "picow/button"

# function to read PEM file and return byte array of data
def read_pem(file): # pass the file
    with open(file, "r") as input:
        text = input.read().strip()
        split_text = text.split("\n")
        base64_text = "".join(split_text[1:-1])
        return ubinascii.a2b_base64(base64_text)
    
# callback function to handle received MQTT messages
def on_mqtt_msg(topic, msg):
    topic_str = topic.decode()
    msg_str = msg.decode() # convert from bytes to str
    print(f"RX: {topic_str}\n\t{msg_str}")

    #-----------Process Mesaage
    if topic_str is MQTT_LED_TOPIC:
        if msg_str is "on":
            led.on()
        elif msg_str is "off":
            led.off()
        elif msg_str is "toggle":
            led.toggle()