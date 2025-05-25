import psycopg2
import os
import shutil
from app.config import settings

# Connect to the database
conn = psycopg2.connect(settings.DATABASE_URL)
cursor = conn.cursor()

# Drop alembic_version table if it exists
cursor.execute("""
DROP TABLE IF EXISTS alembic_version;
""")
conn.commit()
conn.close()

print("Dropped alembic_version table")

# Remove alembic directory
if os.path.exists("alembic"):
    shutil.rmtree("alembic")
    print("Removed alembic directory")

# Create alembic directory structure
os.system("alembic init alembic")
print("Initialized new alembic directory")

# Update alembic.ini
with open("alembic.ini", "r") as f:
    content = f.read()

content = content.replace(
    "sqlalchemy.url = driver://user:pass@localhost/dbname",
    f"sqlalchemy.url = {settings.DATABASE_URL}"
)

with open("alembic.ini", "w") as f:
    f.write(content)

print("Updated alembic.ini")

# Update env.py
env_py_content = """from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Import your models
from app.models import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    \"\"\"Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    \"\"\"
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    \"\"\"Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    \"\"\"
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
"""

with open("alembic/env.py", "w") as f:
    f.write(env_py_content)

print("Updated env.py")

# Create a manual migration file
os.makedirs("alembic/versions", exist_ok=True)
migration_content = """\"\"\"initial migration

Revision ID: initial_migration
Revises: 
Create Date: 2023-05-15 10:00:00.000000

\"\"\"
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'initial_migration'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types first
    user_role = postgresql.ENUM('ADMIN', 'DOCTOR', 'PATIENT', 'STAFF', name='userrole')
    user_status = postgresql.ENUM('ACTIVE', 'INACTIVE', 'PENDING', name='userstatus')
    
    user_role.create(op.get_bind())
    user_status.create(op.get_bind())
    
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=False),
        sa.Column('role', sa.Enum('ADMIN', 'DOCTOR', 'PATIENT', 'STAFF', name='userrole'), nullable=False),
        sa.Column('status', sa.Enum('ACTIVE', 'INACTIVE', 'PENDING', name='userstatus'), nullable=False, server_default='PENDING'),
        sa.Column('disabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    
    # Create indexes
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_user_id'), 'users', ['user_id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_user_id'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    
    # Drop table
    op.drop_table('users')
    
    # Drop enum types
    sa.Enum(name='userstatus').drop(op.get_bind())
    sa.Enum(name='userrole').drop(op.get_bind())
"""

with open("alembic/versions/initial_migration.py", "w") as f:
    f.write(migration_content)

print("Created initial migration file")
print("Now run: alembic upgrade head")