from config.config import Config
from databases import Database

config = Config()
database = Database(config.DATABASE_URL)