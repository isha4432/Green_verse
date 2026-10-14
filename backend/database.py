import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from config import settings

logger = logging.getLogger("green_verse.database")

class Database:
    client: AsyncIOMotorClient = None
    db = None
    is_connected: bool = False

    # In-memory fallback stores when MongoDB is offline
    memory_store = {
        "users": [],
        "farmers": [],
        "farms": [],
        "plots": [],
        "crop_guides": [],
        "certificates": [],
        "experiments": [],
        "irrigation_plans": [],
        "climate_scenarios": [],
        "quantum_runs": [],
        "soil_records": [],
        "water_records": []
    }

db_manager = Database()

async def connect_to_mongo():
    try:
        db_manager.client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=2000
        )
        # Verify connection
        await db_manager.client.admin.command('ping')
        db_manager.db = db_manager.client[settings.DATABASE_NAME]
        db_manager.is_connected = True
        logger.info(f"Connected to MongoDB at {settings.MONGODB_URI}, database: {settings.DATABASE_NAME}")
    except (ConnectionFailure, ServerSelectionTimeoutError, Exception) as e:
        db_manager.is_connected = False
        db_manager.db = None
        logger.warning(f"MongoDB connection failed ({e}). Running in resilient fallback mode (in-memory persistence).")

async def close_mongo_connection():
    if db_manager.client:
        db_manager.client.close()
        logger.info("Closed MongoDB connection.")

def get_db():
    return db_manager.db
