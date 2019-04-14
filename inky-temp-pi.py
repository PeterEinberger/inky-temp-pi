#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import argparse
import Adafruit_DHT
from datetime import datetime
from inky import InkyPHAT
from PIL import Image, ImageDraw, ImageFont
from font_fredoka_one import FredokaOne

try:
    import requests
except ImportError:
    exit("This script requires the requests module\nInstall with: sudo pip install requests")


print("""Inky pHAT: Weather

Displays weather information for a specific sensor.

""")

# Command line arguments to set display colour

parser = argparse.ArgumentParser()
parser.add_argument('--colour', '-c', type=str, required=True, choices=["red", "black", "yellow"], help="ePaper display colour")
args = parser.parse_args()

dirPath = os.path.dirname(__file__)
serviceUrl = "http://192.168.1.174:3000"

# Settings for TempHumid Sensor

dht = Adafruit_DHT.DHT11
dhtPin = 14

# Set up the display

colour = args.colour
inky_display = InkyPHAT(colour)
inky_display.set_border(inky_display.BLACK)

WARNING_TEMP = 25.0

def get_weather():
    weather = {}
    res = requests.get(serviceUrl + "/probe")
    if res.status_code == 200:
        curr = res.json()
        weather["temperature"] = curr['temp']
        weather["humidity"] = curr['humidity']
        weather["time"] = curr['date']
        return weather
    else:
        return weather

def create_mask(source, mask=(inky_display.WHITE, inky_display.BLACK, inky_display.RED)):
    """Create a transparency mask.

    Takes a paletized source image and converts it into a mask
    permitting all the colours supported by Inky pHAT (0, 1, 2)
    or an optional list of allowed colours.

    :param mask: Optional list of Inky pHAT colours to allow.

    """
    mask_image = Image.new("1", source.size)
    w, h = source.size
    for x in range(w):
        for y in range(h):
            p = source.getpixel((x, y))
            if p in mask:
                mask_image.putpixel((x, y), 255)

    return mask_image

def read_dht11():
    humidity, temperature = Adafruit_DHT.read_retry(dht, dhtPin)
    print(humidity)
    print(temperature)

# Dictionaries to store our icons and icon masks in
icons = {}
masks = {}

weather = get_weather()

read_dht11()

# This maps the weather summary from Dark Sky
# to the appropriate weather icons
icon_map = {
    "snow": ["snow", "sleet"],
    "rain": ["rain"],
    "cloud": ["fog", "cloudy", "partly-cloudy-day", "partly-cloudy-night"],
    "sun": ["clear-day", "clear-night"],
    "storm": [],
    "wind": ["wind"]
}

# Placeholder variables
humidity = 0
temperature = 0
weather_icon = "sun"

if weather:
    temperature = weather["temperature"]
    humidity = weather["humidity"]
    time_string = weather["time"]

#     for icon in icon_map:
#         if summary in icon_map[icon]:
#             weather_icon = icon
#             break

else:
    print("Warning, no weather information found!")

# Create a new canvas to draw on
img = Image.open(dirPath + "resources/backdrop.png")
draw = ImageDraw.Draw(img)

# Load our icon files and generate masks
for icon in glob.glob(dirPath + "resources/icon-*.png"):
    icon_name = icon.split("icon-")[1].replace(".png", "")
    icon_image = Image.open(icon)
    icons[icon_name] = icon_image
    masks[icon_name] = create_mask(icon_image)

# Load the FredokaOne font
font = ImageFont.truetype(FredokaOne, 22)

# Draw lines to frame the weather data
draw.line((69, 36, 69, 81))       # Vertical line
draw.line((31, 35, 184, 35))      # Horizontal top line
draw.line((69, 58, 174, 58))      # Horizontal middle line
draw.line((169, 58, 169, 58), 2)  # Red seaweed pixel :D

# Write text with weather values to the canvas
# time_string = time_string.replace(' (Central European Standard Time)', '')
# time_string = datetime.(time_string, "%H:%M:%S %Z%z").strftime("%H:%M")
time_string = datetime.utcfromtimestamp(time_string).strftime('%H:%M     %d.%m')

draw.text((36, 12), time_string, inky_display.WHITE, font=font)

draw.text((72, 34), "T", inky_display.WHITE, font=font)
draw.text((92, 34), u"{}°".format(temperature), inky_display.WHITE if temperature < WARNING_TEMP else inky_display.RED, font=font)

draw.text((72, 58), "H", inky_display.WHITE, font=font)
draw.text((92, 58), u"{}%".format(humidity), inky_display.WHITE, font=font)

# Draw the current weather icon over the backdrop
if weather_icon is not None:
    img.paste(icons[weather_icon], (28, 36), masks[weather_icon])

else:
    draw.text((28, 36), "?", inky_display.RED, font=font)

# Display the weather data on Inky pHAT
inky_display.set_image(img)
inky_display.show()
