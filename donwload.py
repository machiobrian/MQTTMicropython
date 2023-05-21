import mip 
import time 
import network

SSID = "_braen"
PASS = "1234567890"
wlan = network.WLAN(network.STA_IF)

print(f"Connecting to WiFi SSID: {SSID}")
wlan.active(True)
wlan.connect(SSID, PASS)

while not wlan.isconnected():
    time.sleep(0.5)
print("Connected")

mip.install("https://raw.githubusercontent.com/micropython/micropython-lib/master/micropython/umqtt.simple/umqtt/simple.py")

