from os import getenv

from dotenv import load_dotenv

load_dotenv()

API_ID = "6435225"
# -------------------------------------------------------------
API_HASH = "4e984ea35f854762dcde906dce426c2d"
# --------------------------------------------------------------
BOT_TOKEN = getenv("BOT_TOKEN", "8113054986:AAGhPZs8lTovJQ2Cc-RlnwTY8UMC5UdOBmc")
STRING1 = getenv("STRING_SESSION", None)
MONGO_URL = getenv("MONGO_URL", "mongodb+srv://BADMUNDA:BADMYDAD@badhacker.i5nw9na.mongodb.net/")
OWNER_ID = int(getenv("OWNER_ID", "7588172591"))
SUPPORT_GRP = getenv("SUPPORT_GRP", "PBX_CHAT")
UPDATE_CHNL = getenv("UPDATE_CHNL", "HEROKUBIN_01")
OWNER_USERNAME = getenv("OWNER_USERNAME", "II_BAD_BABY_II")
API = getenv("API", "http://3.0.146.239:8000/chatbot?api_key=chatai.Badmunda.workers&message=")
