import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN", "")
print(repr(token))
