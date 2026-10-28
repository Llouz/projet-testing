import os
# backend/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

URL_BDD = os.environ.get("DATABASE_URL", "sqlite:///./application-demo.db")

moteur = create_engine(URL_BDD)
SessionLocale = sessionmaker(autocommit=False, autoflush=False, bind=moteur)

Base = declarative_base()
