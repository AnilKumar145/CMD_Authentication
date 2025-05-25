"""initial migration

Revision ID: initial_migration
Revises: 
Create Date: 2023-05-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = 'initial_migration'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Get connection
    connection = op.get_bind()
    
    # Check if enum types exist
    result = connection.execute(text("""
        SELECT EXISTS (
            SELECT 1 FROM pg_type 
            WHERE typname = 'userrole'
        );
    """))
    userrole_exists = result.scalar()
    
    result = connection.execute(text("""
        SELECT EXISTS (
            SELECT 1 FROM pg_type 
            WHERE typname = 'userstatus'
        );
    """))
    userstatus_exists = result.scalar()
    
    # Create enum types if they don't exist
    if not userrole_exists:
        connection.execute(text("""
            CREATE TYPE userrole AS ENUM ('ADMIN', 'DOCTOR', 'PATIENT', 'STAFF');
        """))
    
    if not userstatus_exists:
        connection.execute(text("""
            CREATE TYPE userstatus AS ENUM ('ACTIVE', 'INACTIVE', 'PENDING');
        """))
    
    # Check if users table already exists
    result = connection.execute(text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'users'
        );
    """))
    users_table_exists = result.scalar()
    
    # Only create users table if it doesn't exist
    if not users_table_exists:
        # Create users table directly with enum types
        connection.execute(text("""
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR NOT NULL UNIQUE,
                username VARCHAR NOT NULL UNIQUE,
                email VARCHAR NOT NULL UNIQUE,
                hashed_password VARCHAR NOT NULL,
                full_name VARCHAR NOT NULL,
                role userrole NOT NULL,
                status userstatus NOT NULL DEFAULT 'PENDING',
                disabled BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE,
                last_login TIMESTAMP WITH TIME ZONE
            );
        """))
        
        # Create indexes
        connection.execute(text("""
            CREATE INDEX ix_users_id ON users (id);
            CREATE INDEX ix_users_user_id ON users (user_id);
            CREATE INDEX ix_users_username ON users (username);
            CREATE INDEX ix_users_email ON users (email);
        """))


def downgrade() -> None:
    connection = op.get_bind()
    
    # Drop indexes
    connection.execute(text("""
        DROP INDEX IF EXISTS ix_users_email;
        DROP INDEX IF EXISTS ix_users_username;
        DROP INDEX IF EXISTS ix_users_user_id;
        DROP INDEX IF EXISTS ix_users_id;
    """))
    
    # Drop table
    connection.execute(text("DROP TABLE IF EXISTS users;"))
