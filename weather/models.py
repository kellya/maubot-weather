"""
Data models for weather information.
"""

from typing import Optional


class WeatherData:
    """Class to standardize weather data across providers"""

    def __init__(
        self,
        location: str,
        temperature: str,
        condition: str,
        humidity: str = None,
        wind: str = None,
        forecast: str = None,
        image_url: str = None,
        provider_link: str = None,
    ):
        self.location = location
        self.temperature = temperature
        self.condition = condition
        self.humidity = humidity
        self.wind = wind
        self.forecast = forecast
        self.image_url = image_url
        self.provider_link = provider_link

    def get_formatted_message(self) -> str:
        """Return a formatted message with the weather information"""
        if self.temperature:
            message = f"{self.location}: {self.temperature}, {self.condition}"
        else:
            # For wttr.in and other providers that may not separate temperature
            message = f"{self.location}: {self.condition}"

        if self.humidity:
            message += f", Humidity: {self.humidity}"

        if self.wind:
            message += f", Wind: {self.wind}"

        if self.forecast:
            message += f"\nForecast: {self.forecast}"

        if self.provider_link:
            message += f" ([source]({self.provider_link}))"

        return message


class MoonPhaseData:
    """Class to standardize moon phase data across providers"""

    def __init__(self, phase: str, illumination: str, icon: str = None):
        self.phase = phase
        self.illumination = illumination
        self.icon = icon

    def get_formatted_message(self) -> str:
        """Return a formatted message with the moon phase information"""
        if self.icon:
            return f"{self.icon} {self.phase} ({self.illumination}% Illuminated)"
        return f"{self.phase} ({self.illumination}% Illuminated)"
