from dotenv import load_dotenv
from os import environ
try: load_dotenv()
except Exception as e: print(e)
BOT_TOKEN : str = environ.get("BOT_TOKEN")
YOOMONEY_CLIENT_ID : str = environ.get("YOOMONEY_CLIENT_ID")
YOOMONEY_CLIENT_SECRET : str = environ.get("YOOMONEY_CLIENT_SECRET")
YOOMONEY_ACCESS_TOKEN : str = environ.get("YOOMONEY_ACCESS_TOKEN")
YOOMONEY_WALLET_ID : str = environ.get("YOOMONEY_WALLET_ID")
FLASK_URL : str = "http://localhost:5000"; TOKEN_PASS : str = environ.get("TOKEN_PASS")