from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./aml_database.db"


#  gateaway between Python and db
#  doesn't connect immediately, only when a session requests it
#  check_some_thread = False allows diff threads to share the same engine
#  otherwise each engine requires its own thread
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})


#  directs the session to our data base
#  i want to commit and flush on my own
#  its the real conversation with our db
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


#  basic class, AmlReport inherits from it to be registered that it exists
Base = declarative_base()


def get_db():
    db = SessionLocal()  # opens a live conversation with db
    try:
        yield db  # hands session to route from FastAPI and waits until its done
    finally:  # finally means line runs no matter what
        db.close()  # closes the session


# reads Base registry and builds all tables in the .db file if they dont exist yet
# in base register there are only classes which inherit from Base
Base.metadata.create_all(bind=engine)
