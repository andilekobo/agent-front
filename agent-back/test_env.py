from dotenv import load_dotenv
import os

load_dotenv()

print("App ID loaded:", bool(os.getenv("ADZUNA_APP_ID")))
print("App Key loaded:", bool(os.getenv("ADZUNA_APP_KEY")))