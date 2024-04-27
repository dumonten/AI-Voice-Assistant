from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import settings

SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{settings.PG_USER}:{settings.PG_PASSWD}@{settings.PG_HOST}:{settings.PG_PORT}/{settings.PG_DB}"

print(SQLALCHEMY_DATABASE_URL)

# Create an async engine
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)

# Create a sessionmaker bound to the async engine
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Define your declarative base
Base = declarative_base()
