"""
Abstract base class for weather providers.
"""

from abc import ABC, abstractmethod
from typing import Optional

from ..models import WeatherData, MoonPhaseData


class WeatherProvider(ABC):
    """Abstract base class for weather providers"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Get provider name"""
        pass

    @property
    def supports_images(self) -> bool:
        """Whether this provider supports weather images"""
        return False

    @abstractmethod
    async def get_weather(
        self, location: str, units: str = None, language: str = None
    ) -> WeatherData:
        """Get weather data for a location"""
        pass

    @abstractmethod
    async def get_weather_image(
        self, location: str, units: str = None, language: str = None
    ) -> Optional[bytes]:
        """Get weather image for a location, return None if not supported"""
        pass

    @abstractmethod
    async def get_moon_phase(self) -> MoonPhaseData:
        """Get current moon phase data"""
        pass
