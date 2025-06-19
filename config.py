from os import getenv

from dotenv import load_dotenv

load_dotenv()

API_ID = "6435225"
# -------------------------------------------------------------
API_HASH = "4e984ea35f854762dcde906dce426c2d"
# --------------------------------------------------------------
BOT_TOKEN = getenv("BOT_TOKEN", "7420275716:AAHUxjzAerHvQEVIzzRY_7by_Iu84U_CShY")
STRING1 = getenv("STRING_SESSION", None)
MONGO_URL = getenv("MONGO_URL", "mongodb+srv://BADMUNDA:BADMYDAD@badhacker.i5nw9na.mongodb.net/")
OWNER_ID = int(getenv("OWNER_ID", "7650291301"))
SUPPORT_GRP = getenv("SUPPORT_GRP", "ZOYU_SUPPORT")
UPDATE_CHNL = getenv("UPDATE_CHNL", "THE_INCRICIBLE")
OWNER_USERNAME = getenv("OWNER_USERNAME", "LEGEND_MICKEY")
API = getenv("API", "http://3.0.146.239:8000/chatbot?api_key=chatai.Badmunda.workers&message=")
