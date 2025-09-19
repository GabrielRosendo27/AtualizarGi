from dotenv import load_dotenv
import os


load_dotenv()

PORTAL_URL = os.getenv("PORTAL_URL")
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR")
TARGET_DIR = os.getenv("TARGET_DIR")
FILES_TO_COPY = os.getenv("FILES_TO_COPY")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
SECRET = os.getenv("SECRET")
