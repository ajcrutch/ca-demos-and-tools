"""Database configuration and session management."""

import logging

import google.cloud.sql.connector
from prism.server.config import settings
import sqlalchemy
import sqlalchemy.orm

logger = logging.getLogger(__name__)

# Lazy initialize connector
_connector = None


def get_conn():
  """Creates a connection using the Cloud SQL Connector if configured."""
  global _connector
  logger.info("get_conn called: instance=%s", settings.instance_connection_name)
  if settings.instance_connection_name:
    if _connector is None:
      # Initialize Connector with a higher timeout for cold starts
      _connector = google.cloud.sql.connector.Connector(timeout=60)

    logger.info(
        "Attempting Cloud SQL connection: instance=%s, db=%s, user=%s,"
        " ip_type=%s",
        settings.instance_connection_name,
        settings.db_name,
        settings.db_user,
        settings.db_ip_type,
    )
    return _connector.connect(
        settings.instance_connection_name,
        "pg8000",
        user=settings.db_user,
        password=settings.db_pass.replace("\n", "").strip()
        if settings.db_pass
        else "",
        db=settings.db_name,
        ip_type=settings.db_ip_type,
    )
  logger.info("No instance_connection_name, returning None")
  return None


logging.info("")

# Create engine with optional custom creator
if settings.instance_connection_name:
  engine = sqlalchemy.create_engine(
      settings.final_database_url,
      creator=get_conn,
  )
else:
  engine = sqlalchemy.create_engine(
      settings.final_database_url,
  )

SessionLocal = sqlalchemy.orm.sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

Base = sqlalchemy.orm.declarative_base()


def get_db():
  """Dependency for getting DB session."""
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()
