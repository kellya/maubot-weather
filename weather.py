"""bot do things"""

import requests
from maubot import Plugin, MessageEvent
from maubot.handlers import command
from typing import Type
from mautrix.util.config import BaseProxyConfig, ConfigUpdateHelper


class Config(BaseProxyConfig):
    def do_update(self, helper: ConfigUpdateHelper) -> None:
        helper.copy("show_link")
        helper.copy("default_location")


class WeatherBot(Plugin):
    async def start(self) -> None:
        await super().start()
        self.config.load_and_update()

    @classmethod
    def get_config_class(cls) -> Type[BaseProxyConfig]:
        return Config

    @command.new("weather", help="Get the weather")
    @command.argument("location", pass_raw=True)
    async def weather_handler(self, evt: MessageEvent, location=None) -> None:
        # This is a mess of redundancy that needs cleaned up, but it is working
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
            weather = requests.get(f'http://wttr.in/{location}?format=3').text
            link = f'[(wttr.in)](http://wttr.in/{location})'
            message = weather
            if self.config["show_link"]:
                message += link
            await evt.respond(message)
        else:
            if self.config["default_location"]:
                location=self.config["default_location"]
            weather = requests.get(f'http://wttr.in/{location}?format=3').text
            link = f'[(wttr.in)](http://wttr.in/{location})'
            message = weather
            if self.config["show_link"]:
                message += link
            await evt.respond(message)
