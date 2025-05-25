import psycopg2
from app.config import settings

# Connect to the database
conn = psycopg2.connect(settings.DATABASE_URL)
cursor = conn.cursor()

# Check if alembic_version table exists
cursor.execute("""
SELECT EXISTS (
   SELECT FROM information_schema.tables 
   WHERE table_name = 'alembic_version'
);
""")

exists = cursor.fetchone()[0]
print(f"alembic_version table exists: {exists}")

if exists:
    # Check current version
    cursor.execute("SELECT version_num FROM alembic_version;")
    version = cursor.fetchone()
    print(f"Current version: {version}")

conn.close()