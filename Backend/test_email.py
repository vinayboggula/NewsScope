import os
from dotenv import load_dotenv

load_dotenv()

print("MY_EMAIL =", os.getenv("MY_EMAIL"))
print("MY_PASSWORD =", os.getenv("APP_PASSWORD"))
print("TO_EMAIL =", os.getenv("TO_EMAIL"))
