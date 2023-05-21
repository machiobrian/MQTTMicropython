import network
import time 
import machine 
import ssl 
import ubinascii

from machine import Pin, Timer
import ntptime 
from simple import MQTTClient

SSID = "_braen"
PASS = "1234567890"

MQTT_CLIENT_KEY ="private.pem.key"
MQTT_CLIENT_ID = ubinascii.hexlify(machine.unique_id())
MQTT_CLIENT_CERT = "certificate.pem.crt"

MQTT_BROKER = "a7tk9sth503zl-ats.iot.us-east-1.amazonaws.com"
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

# callback funciton to handle changes in button state
# publishes "released" or "pressed" message
def publish_mqtt_button_msg(t):
    topic_str = MQTT_BUTTON_TOPIC
    msg_str = "released" if button.value() else "pressed"
    print(f"TX: {topic_str}\n\t{msg_str}")
    mqtt_client.publish(topic_str, msg_str)

# callback function to periodically send MQTT ping messages
# to the MQTT broker
def send_mqtt_ping(t):
    print("TX: ping")
    mqtt_client.ping()

# read data in the private key, public cert. root CA files
key = read_pem(MQTT_CLIENT_KEY)
cert = read_pem(MQTT_CLIENT_CERT)
ca = read_pem(MQTT_BROKER_CA)

# create pin objects for on-board LED and external button
led = Pin("LED", Pin.OUT)
button = Pin(3, Pin.IN, Pin.PULL_UP)

# init the wifi interface
wlan = network.WLAN(network.STA_IF)

# create MQTT client that use TLS/SSL for a secure connection
mqtt_client = MQTTClient(
    MQTT_CLIENT_ID,
    MQTT_BROKER,
    keepalive=60,
    ssl=True,
    ssl_params={
        "server_hostname": MQTT_BROKER,
        "key": key,
        "cert": cert,
        "cert_reqs": ssl.CERT_REQUIRED,
        "cadata": ca,
        
    },
)
print(f"Connecting to WiFi SSID: {SSID}")

# activate and connect to WiFi network
wlan.active(True)
wlan.connect(SSID, PASS)

while not wlan.isconnected():
    time.sleep(0.5)

print(f"Connect to WiFi SSID: {SSID}")

# update the current time on the board using NTP
ntptime.settime()
print(f"Connecting to MQTT Broker.")

# register callback to/for MQTT messages, connect to broker and
# sub to LED topic
mqtt_client.set_callback(on_mqtt_msg)
mqtt_client.connect()
mqtt_client.subscribe(MQTT_LED_TOPIC)

# register callback function to handle changes in button state
button.irq(publish_mqtt_button_msg, Pin.IRQ_FALLING | Pin.IRQ_RISING)

# turn on-board LED on 
led.on() 

# create timer for periodic MQTT ping messages for keep-alive
mqtt_ping_timer = Timer(
    mode = Timer.PERIODIC,
    period = mqtt_client.keepalive*1000,
    callback = send_mqtt_ping
)

# main loop, that continuously checks for incoming MQTT messages
while True:
    mqtt_client.check_msg()