import os
from dotenv import load_dotenv
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=env_path, verbose=True)

TELEGRAM_BOT_MODE = os.getenv("TELEGRAM_BOT_MODE", "pollingx")

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHROME_BINARY_PATH = os.getenv("CHROME_BINARY_PATH")
CHROMEDRIVER_EXECUTABLE_PATH = os.getenv("CHROMEDRIVER_EXECUTABLE_PATH")
DB_SERVER = os.getenv("MONGO_DB_SERVER", "mongodb://127.0.0.1:27017/")