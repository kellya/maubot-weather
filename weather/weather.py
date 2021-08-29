""" maubot to get the weather from wttr.in and post in matrix chat """

from typing import Type
from maubot import Plugin, MessageEvent
from maubot.handlers import command
from mautrix.util.config import BaseProxyConfig, ConfigUpdateHelper
from yarl import URL


class Config(BaseProxyConfig):
    """Configuration class"""

    def do_update(self, helper: ConfigUpdateHelper) -> None:
        helper.copy("show_link")
        helper.copy("default_location")
        helper.copy("show_image")


class WeatherBot(Plugin):
    """maubot plugin class to get the weather and respond in a chat"""

    async def start(self) -> None:
        await super().start()
        self.config.load_and_update()

    @classmethod
    def get_config_class(cls) -> Type[BaseProxyConfig]:
        return Config

    @command.new(name="weather", help="Get the weather")
    @command.argument("location", pass_raw=True)
    async def weather_handler(self, evt: MessageEvent, location=None) -> None:
        """Listens for !weather and returns a message with the result of
        a call to wttr.in for the location specified by !weather <location>
        or by the config file if no location is given"""
        if location and location == "help":
            await evt.respond(
                """
                          Uses wttr.in to get the weather and respond. If you
                          don't specify a location, it will use the IP address
                          of the server to figure out what the location is.

                          Otherwise, you may specify the location by name:
                          !weather Chicago

                          or by Airport Code
                          !weather SFO
                          """
            )
        elif not location:
            if self.config["default_location"]:
                location = self.config["default_location"]

        resp = await self.http.get(f"http://wttr.in/{location}?format=3")
        weather = await resp.text()
        message = weather
        if self.config["show_link"]:
            link = f'[(wttr.in)]({URL("https://wttr.in") / location})'
            message += link
        if weather.startswith("Unknown location; please try"):
            message += (
                " | Note: "
                "An 'unknown location' likely indicates "
                "an issue with wttr.in obtaining geolocation information. "
                "This issue will probably resolve itself, so sit "
                "tight and look out the window until it does"
            )
        await evt.respond(message)
        if self.config["show_image"]:
            wttr_url = "http://wttr.in"
            wttr_location = location.replace(", ", "_")
            wttr_location = location.replace(" ", "_")
            wttr = f"{wttr_url}/{wttr_location}.png"
            resp = await self.http.get(wttr)
            if resp.status == 200:
                data = await resp.read()
                filename = "weather.png"
                uri = await self.client.upload_media(
                    data, mime_type="image/png", filename="filename"
                )
                await self.client.send_image(
                    evt.room_id,
                    url=uri,
                    file_name=filename,
                )
            else:
                await evt.respond("error getting location " + wttr)

    @command.new(name="moon", help="Get the moon phase")
    async def moon_phase_handler(
        self,
        evt: MessageEvent,
    ) -> None:
        """Get the lunar phase from wttr.in and respond in chat"""
        evt.respond("getting moon phase")
        resp = await self.http.get("http://wttr.in/Moon?format=%m")
        moon_phase = await resp.text()
        await evt.respond(f"Moon Phase: {moon_phase}")
