from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING as ASC, DESCENDING as DESC
from os import environ

try:
    load_dotenv()
except Exception as e:
    print(e)

mongodb_uri = environ.get("MONGODB_URI")
database_name = environ.get("DATABASE_NAME", "test")  
TOKEN_PASS_HASH : str = environ.get("TOKEN_PASS_HASH")
CRYPT_KEY : str = environ.get("CRYPT_KEY")

MOSCOW_UTC_OFFSET : int = 3

ARIZONA_SERVERS : list[dict[str, str]] = [
    {"name": "Phoenix", "ip": "185.169.134.3:7777"},
    {"name": "Tucson", "ip": "185.169.134.4:7777"},
    {"name": "Scottdale", "ip": "185.169.134.43:7777"}, 
    {"name": "Chandler", "ip": "185.169.134.44:7777"},
    {"name": "Brainburg", "ip": "185.169.134.45:7777"},
    {"name": "Saint Rose", "ip": "185.169.134.5:7777"},
    {"name": "Mesa", "ip": "185.169.134.59:7777"},
    {"name": "Red Rock", "ip": "185.169.134.61:7777"},
    {"name": "Yuma", "ip": "185.169.134.107:7777"},
    {"name": "Surprise", "ip": "185.169.134.109:7777"},
    {"name": "Prescott", "ip": "185.169.134.166:7777"},
    {"name": "Glendale", "ip": "185.169.134.171:7777"},
    {"name": "Kingman", "ip": "185.169.134.172:7777"},
    {"name": "Winslow", "ip": "185.169.134.173:7777"},
    {"name": "Payson", "ip": "185.169.134.174:7777"},
    {"name": "Gilbert", "ip": "80.66.82.191:7777"},
    {"name": "Show-Low", "ip": "80.66.82.190:7777"},
    {"name": "Casa-Grande", "ip": "80.66.82.188:7777"},
    {"name": "Page", "ip": "80.66.82.168:7777"},
    {"name": "Sun City", "ip": "80.66.82.159:7777"},
    {"name": "Queen Creek", "ip": "80.66.82.200:7777"},
    {"name": "Sedona", "ip": "80.66.82.144:7777"},
    {"name": "Holiday", "ip": "80.66.82.132:7777"},
    {"name": "Wednesday", "ip": "80.66.82.128:7777"},
    {"name": "Yava", "ip": "80.66.82.113:7777"},
    {"name": "Faraway", "ip": "80.66.82.82:7777"},
    {"name": "Bumble Bee", "ip": "80.66.82.87:7777"},
    {"name": "Christmas", "ip": "80.66.82.54:7777"},
    {"name": "Mirage", "ip": "80.66.82.39:7777"},
    {"name": "Love", "ip": "80.66.82.33:7777"},
    {"name": "Drake", "ip": "80.66.82.22:7777"},
    {"name" : "Vice City", "ip" : "80.66.82.147:7777"}
]

ARIZONA_IP_LIST = [server_ip["ip"] for server_ip in ARIZONA_SERVERS]

ARIZONA_MAP_URL : str = "https://n-api.arizona-rp.com/api/map"

TOKEN_LIVE_TIME : int = 60*60*24*30

class Prop:
    def __init__(self, title : str, price : int) -> None:
        self.title = title
        self.price = price


class PROPS:
    HOUSE : Prop = Prop(title="HOUSE", price=104_000)
    BUSINESS : Prop = Prop(title="BUSINESS", price=250_000)


try:
    mongodb_client = AsyncIOMotorClient(mongodb_uri, uuidRepresentation="standard")
    database = mongodb_client[database_name]
    tokens_table = database["tokens"]
    payday_stats_table = database["payday_stats"]

    
    async def check_connection():
        await mongodb_client.admin.command('ping')
        print("Successfully connected to MongoDB")

except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
