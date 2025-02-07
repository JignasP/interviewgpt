"""Configuration file for the application"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# UI Configuration
UI_CONFIG = {
    'WINDOW_SIZE': '1000x800',
    'MIN_WINDOW_SIZE': (900, 700),
    'DARK_BG': '#1a1a1a',
    'SUCCESS_COLOR': '#00ff99',
    'WARNING_COLOR': '#ffaa00',
    'ERROR_COLOR': '#ff3333',
    'DISABLED_COLOR': '#888888',
    'BUTTON_HEIGHT': 40,
    'FONT_FAMILY': 'Roboto',
}