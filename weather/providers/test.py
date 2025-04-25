"""
Mock weather provider for testing purposes.
"""

from typing import Optional

from .base import WeatherProvider
from ..weather import WeatherData, MoonPhaseData


class TestProvider(WeatherProvider):
    """Mock weather provider for testing purposes"""

    def __init__(self, http_client):
        self.http = http_client

    @property
    def name(self) -> str:
        return "test"

    @property
    def supports_images(self) -> bool:
        return False

    async def get_weather(
        self, location: str, units: str = None, language: str = None
    ) -> WeatherData:
        """Return fake weather data for testing"""
        # Generate some simple test data
        temp_unit = "°F" if units == "u" else "°C"
        temperature = f"72{temp_unit}" if units == "u" else f"22{temp_unit}"

        # Customize messages based on language if provided
        greeting = (
            "Sunny day in" if not language or language == "en" else "Día soleado en"
        )

        return WeatherData(
            location="TestCity",
            temperature=temperature,
            condition="Sunny with test clouds",
            humidity="50%",
            wind="5 mph" if units == "u" else "8 km/h",
            forecast=f"{greeting} TestCity",
            provider_link="https://example.com/test-weather",
        )

    async def get_weather_image(
        self, location: str, units: str = None, language: str = None
    ) -> Optional[bytes]:
        """Test provider doesn't support images"""
        return None

    async def get_moon_phase(self) -> MoonPhaseData:
        """Return fake moon phase data for testing"""
        return MoonPhaseData(phase="Test Moon", illumination="42", icon="🌔")
