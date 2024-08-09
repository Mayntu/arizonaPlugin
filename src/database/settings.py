from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import os

try:
    load_dotenv()
except Exception as e:
    print(e)

mongodb_uri = os.environ.get("MONGODB_URI")
database_name = os.environ.get("DATABASE_NAME", "test")  

try:
    mongodb_client = AsyncIOMotorClient(mongodb_uri)
    database = mongodb_client[database_name]
    tokens_table = database["tokens"]

    
    async def check_connection():
        await mongodb_client.admin.command('ping')
        print("Successfully connected to MongoDB")

except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
