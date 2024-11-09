import os

class Config:
    API_KEY = os.getenv('API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    # Add other configuration variables as needed
