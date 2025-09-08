import os
from dataclasses import dataclass, field
from dateutil import tz
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    ADMIN_IDS: set[int] = field(default_factory=lambda: {
        int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()
    })
    TZ = tz.gettz("Europe/Rome")
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    FILES_DIR = os.path.join(DATA_DIR, "files")
    REPORTS_DIR = os.path.join(BASE_DIR, "reports")
    TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
    DB_PATH = os.path.join(DATA_DIR, "bot.db")

settings = Settings()

# Ensure dirs exist
os.makedirs(settings.FILES_DIR, exist_ok=True)
os.makedirs(settings.REPORTS_DIR, exist_ok=True)
