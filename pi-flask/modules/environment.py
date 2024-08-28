import os
from dotenv import load_dotenv

load_dotenv(override=True)


PI_API_KEY=os.getenv("PI_API_KEY")
DEVELOPMENT_MODE=os.getenv("DEVELOPMENT_MODE")