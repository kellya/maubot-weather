""" maubot to get the weather from wttr.in and post in matrix chat """

from __future__ import annotations
from typing import Type
from maubot import Plugin, MessageEvent
from maubot.handlers import command
from mautrix.util.config import BaseProxyConfig, ConfigUpdateHelper
from mautrix.util.async_db import UpgradeTable, Connection
from yarl import URL

upgrade_table = UpgradeTable()


@upgrade_table.register(description="Initial revision")
async def upgrade_v1(conn: Connection) -> None:
    await conn.execute(
        """CREATE TABLE wx_location_pref (
            username   TEXT PRIMARY KEY,
            city TEXT NOT NULL
        )"""
    )


@upgrade_table.register(description="Remember user who added value")
async def upgrade_v2(conn: Connection) -> None:
    await conn.execute("ALTER TABLE wx_location_pref ADD COLUMN creator TEXT")


@upgrade_table.register(description="Remember user who added value")
async def upgrade_v3(conn: Connection) -> None:
    await conn.execute(
        "insert into wx_location_pref values('default','Columbus, OH','')"
    )


class Config(BaseProxyConfig):
    """Configuration class"""

    def do_update(self, helper: ConfigUpdateHelper) -> None:
        helper.copy("show_link")
        helper.copy("default_location")
        helper.copy("show_image")
        helper.copy("default_units")


class WeatherBot(Plugin):
    """maubot plugin class to get the weather and respond in a chat"""

    async def start(self) -> None:
        await super().start()
        self.config.load_and_update()

    @classmethod
    def get_db_upgrade_table(cls) -> UpgradeTable | None:
        return upgrade_table

    @classmethod
    def get_config_class(cls) -> Type[BaseProxyConfig]:
        return Config

    def get_location(self, location=None) -> str:
        """Return a cleaned-up location name"""
        if not location:
            location = self.config["default_location"]
        location = location.replace(", ", "_")
        location = location.replace(" ", "+")
        return location.strip()

    async def get_weather(self, location, units=None) -> str:
        if self.config["default_units"]:
            units = f"&{self.config['default_units']}"
        if "u:" in location:
            # If the location has units specified, attempt to use them
            location, custom_unit = location.split("u:")
            if custom_unit in ["u", "m", "M"]:
                units = f"&{custom_unit}"
        location = self.get_location(location.strip())

        resp = await self.http.get(f"http://wttr.in/{location}?format=3{units}")
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
        return message

    @command.new(
        name="weather",
        aliases=("wx",),
        help="Get the weather",
        require_subcommand=False,
    )
    async def weather(self, evt: MessageEvent) -> None:
        message = await self.get_weather("Columbus,Ohio")
        await evt.respond(message)

    @weather.subcommand(name="get")
    @command.argument(name="location", pass_raw=True)
    async def wx_location(self, evt: MessageEvent, location="Columbus,oh") -> None:
        """Listens for !weather and returns a message with the result of
        a call to wttr.in for the location specified by !weather <location>
        or by the config file if no location is given"""
        units = ""  # default to nothing so that response works even if default is unset
        message = await self.get_weather(location)
        await evt.respond(message)
        if self.config["show_image"]:
            wttr_url = "http://wttr.in"
            wttr = URL(f"{wttr_url}/{location}.png?{units}")
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
                await evt.respond(f"error getting location {location}")

    @weather.subcommand(name="help", help="show help")
    async def wx_tips(self, evt: MessageEvent):
        await evt.respond(
            """
                Uses wttr.in to get the weather and respond. If you
                don't specify a location, it will use the IP address
                of the server to figure out what the location is.

                Otherwise, you may specify the location by name:
                !weather Chicago

                or by Airport Code
                !weather SFO

                The units may be specified with a location by adding
                u:<unit> to the end of the location like:
                !weather Chicago u:m

                Where <unit> is one of:
                m = metric
                u = US
                M = metric, but wind in m/s
                """
        )

    @command.new(name="wxpref", help="set weather bot preferences")
    @command.argument("preference", pass_raw=True)
    async def set_prefs(self, evt: MessageEvent, preference):
        """sets preferences in database"""
        q = """
            INSERT INTO wx_location_pref (username, city) VALUES ($1,$2)
            ON CONFLICT (username) DO UPDATE SET username=excluded.username, city=excluded.city
        """
        await self.database.execute(q, evt.sender, preference)
        await evt.respond(f"Inserted {preference} as your default location")

    @command.new(name="moon", help="Get the moon phase")
    async def moon_phase_handler(
            self,
            evt: MessageEvent,
    ) -> None:
        """Get the lunar phase from wttr.in json and respond in chat"""
        # Associate the utf-8 character with the name of the phase
        phase_char = {
            "new moon": "🌑",
            "waxing crescent": "🌒",
            "first quarter": "🌓",
            "waxing gibbous": "🌔",
            "full moon": "🌕",
            "waning gibbous": "🌖",
            "last quarter": "🌗",
            "waning crescent": "🌘",
        }

        resp = await self.http.get(URL(f"http://wttr.in/{self.get_location}?format=j1"))
        # get the JSON data
        moon_phase_json = await resp.json()
        # pull out the "moon_phase"
        moon_phase = moon_phase_json["weather"][0]["astronomy"][0]["moon_phase"]
        # get the character associated with the current phase
        moon_phase_char = phase_char[moon_phase.lower()]
        moon_phase_illum = moon_phase_json["weather"][0]["astronomy"][0][
            "moon_illumination"
        ]
        await evt.respond(
            f"{moon_phase_char} {moon_phase} ({moon_phase_illum}% Illuminated)"
        )
