# Run this script in the auth microservice directory to print the SECRET_KEY
from app.config import settings
print(f"SECRET_KEY: {settings.SECRET_KEY}")