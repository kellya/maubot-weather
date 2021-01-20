from typing import Optional
from time import time
from html import escape
import requests

from mautrix.types import TextMessageEventContent, MessageType, Format, RelatesTo, RelationType

from maubot import Plugin, MessageEvent
from maubot.handlers import command


class WeatherBot(Plugin):
    @command.new("weather", help="Get the weather")
    @command.argument("location", pass_raw=True)
    async def weather_handler(self, evt: MessageEvent, location="") -> None:
        if location and location == "help":
            await evt.respond('''
                          Uses wttr.in to get the weather and respond. If you
                          don't specify a location, it will use the IP address
                          of the server to figure out what the location is.

                          Otherwise, you may specify the location by name:
                          !weather Chicago

                          or by Airport Code
                          !weather SFO
                          ''')
        elif location:
            await evt.respond(
                requests.get(f'http://wttr.in/{location}?format=3').text)
        else:
            await evt.respond(requests.get('http://wttr.in?format=3').text)
