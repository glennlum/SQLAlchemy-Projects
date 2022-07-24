from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from base import Base

"""PostgreSQL"""
# engine = create_engine(
#     # uses local postgres db with psycopg2 adapter
#     # echo = true logs all statements to sys.stdout
#     "postgresql+psycopg2://glennlum:johnnycash@localhost:5432/test_db",
#     echo=True,
# )

"""SQLite"""
engine = create_engine(
    # uses SQLite in-memory DB
    # echo = true logs all statements to sys.stdout
    "sqlite:///:memory:",
    echo=True,
)

"""Initialise DB"""
Base.metadata.create_all(engine)  # creates all tables

"""Session"""
Session = sessionmaker(bind=engine)
session = Session()
