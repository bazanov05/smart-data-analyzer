from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./aml_database.db"


#  creating a physical connection to my SQLite database providing flexible connection
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})


#  directs the session to our data base
#  i want to commit and flush on my own
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


#  basic class, my future class will inherit from it to be automatically added to db
Base = declarative_base()
