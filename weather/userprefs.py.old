from typing import Optional, Dict, Any

class UserPreference:
    """Class to store user preference data"""
    def __init__(
        self,
        user_id: str,
        location: Optional[str] = None,
        units: Optional[str] = None,
        language: Optional[str] = None,
        provider: Optional[str] = None,
        show_image: Optional[bool] = None,
        show_forecast: Optional[bool] = None,
    ):
        self.user_id = user_id
        self.location = location
        self.units = units
        self.language = language
        self.provider = provider
        self.show_image = show_image
        self.show_forecast = show_forecast

    @classmethod
    def from_row(cls, row: Dict[str, Any]):
        return cls(
            user_id=row['user_id'],
            location=row.get('location'),
            units=row.get('units'),
            language=row.get('language'),
            provider=row.get('provider'),
            show_image=row.get('show_image'),
            show_forecast=row.get('show_forecast'),
        )

class UserPreferencesManager:
    """Manager class for user preferences (asyncpg/PostgreSQL)"""
    def __init__(self, db, log):
        self.db = db
        self.log = log

    async def init_db(self) -> None:
        await self.db.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            user_id TEXT PRIMARY KEY,
            location TEXT,
            units TEXT,
            show_image BOOLEAN,
            show_forecast BOOLEAN,
            provider TEXT,
            language TEXT
        )
        ''')

    async def get_preferences(self, user_id: str) -> Optional[UserPreference]:
        row = await self.db.fetchrow(
            "SELECT * FROM user_preferences WHERE user_id = $1", user_id
        )
        if row:
            return UserPreference.from_row(dict(row))
        return None

    async def save_preference(self, user_id: str, key: str, value: Any) -> None:
        # Upsert logic for a single preference
        row = await self.db.fetchrow(
            "SELECT * FROM user_preferences WHERE user_id = $1", user_id
        )
        if row:
            await self.db.execute(
                f"UPDATE user_preferences SET {key} = $1 WHERE user_id = $2",
                value, user_id
            )
        else:
            await self.db.execute(
                f"INSERT INTO user_preferences (user_id, {key}) VALUES ($1, $2)",
                user_id, value
            )

    async def clear_preferences(self, user_id: str) -> None:
        await self.db.execute(
            "DELETE FROM user_preferences WHERE user_id = $1", user_id
        )

    async def load_preferences_with_defaults(self, user_id: str, config: Dict[str, Any], providers: Dict[str, Any]) -> Dict[str, Any]:
        """Load user preferences and merge with server defaults"""
        # Defaults from config
        prefs = {
            'location': config.get('default_location', ''),
            'units': config.get('default_units', ''),
            'language': config.get('default_language', ''),
            'show_image': config.get('show_image', False),
            'provider': config.get('weather_provider', 'wttr.in'),
        }
        # User overrides
        row = await self.get_preferences(user_id)
        if row:
            if row.location:
                prefs['location'] = row.location
            if row.units:
                prefs['units'] = row.units
            if row.language:
                prefs['language'] = row.language
            if row.show_image is not None:
                prefs['show_image'] = row.show_image
            if row.provider and row.provider in providers:
                prefs['provider'] = row.provider
        return prefs
