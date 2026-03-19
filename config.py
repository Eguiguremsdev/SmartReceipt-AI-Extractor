import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class to load and access environment variables."""
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Google Sheets
    GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
    GOOGLE_SPREADSHEET_ID = os.getenv("GOOGLE_SPREADSHEET_ID")
    GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "Sheet1")

    # File paths
    INPUT_DIR = os.getenv("INPUT_DIR", "input")
    PROCESSED_DIR = os.getenv("PROCESSED_DIR", "processed")
    ERROR_LOG = os.getenv("ERROR_LOG", "errors.log")
    DATA_LOG = os.getenv("DATA_LOG", "data_log.csv")

    @classmethod
    def validate(cls):
        """Validate that all required configuration variables are set."""
        missing = []
        if not cls.OPENAI_API_KEY or cls.OPENAI_API_KEY == "your_openai_api_key_here":
            missing.append("OPENAI_API_KEY")
        
        if missing:
            raise ValueError(f"Missing required configuration variables: {', '.join(missing)}\nPlease update your .env file.")

# Ensure directories exist
os.makedirs(Config.INPUT_DIR, exist_ok=True)
os.makedirs(Config.PROCESSED_DIR, exist_ok=True)
