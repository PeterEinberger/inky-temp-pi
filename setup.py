import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "inky-temp-pi",
    version = "0.0.1",
    author = "Katja Bregenzer, Peter Einberger",
    author_email = "",
    description = ("A temperature display using inky phat and dht11"),
    license = "MIT",
    keywords = "rpi zero, inky phat, dht11",
    url = "",
    packages=['inky', 'PIL', 'font_fredoka_one', 'Adafruit_DHT'],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)