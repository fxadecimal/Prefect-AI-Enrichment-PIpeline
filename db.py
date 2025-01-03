#!/usr/bin/env python
import os
import sqlalchemy
from uuid import uuid4
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
import json


import utils
from pathlib import Path
from contextlib import contextmanager
from urllib.parse import urlparse
from slugify import slugify


load_dotenv(".env")

DATABASE_URL = os.getenv("DATABASE_URL")
DEBUG = os.getenv("DEBUG", "True") == "True"

BASE_DIR = Path(__file__).parent
DOWNLOADS_DIR = BASE_DIR / os.getenv("DOWNLOADS_DIR")

# Create engine
engine = create_engine(url=DATABASE_URL, echo=False)

# Create declarative base
Base = declarative_base()


# Create session
def create_session():
    Session = sessionmaker(bind=engine)
    return Session()


def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance


def uid():
    return str(uuid4())


class TimestampedBase(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    created_at = Column(
        DateTime,
        default=func.now(),
    )
    updated_at = Column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
    )


class Downloads(TimestampedBase):
    __tablename__ = "downloads"

    uid = Column(String, default=uid, unique=True)
    type = Column(String, default="default")

    url = Column(String)
    path = Column(String)

    status = Column(String, default="pending")

    downloaded_at = Column(DateTime, nullable=True)
    processed_at = Column(DateTime, nullable=True)

    def download(self):
        domain = slugify(self.url_parsed.netloc)
        _dir = DOWNLOADS_DIR / domain / self.type
        _dir.mkdir(parents=True, exist_ok=True)

        path = _dir / self.uid
        try:
            self.downloaded_at = sqlalchemy.sql.func.now()
            utils.download(self.url, path)
            self.path = str(path.relative_to(DOWNLOADS_DIR))
            self.status = "downloaded"
        except Exception as e:
            self.status = "failed"
        return path

    @contextmanager
    def process(self, session, set_status=True):
        self.status = "processing" if set_status else self.status
        session.commit()
        path = DOWNLOADS_DIR / self.path
        with open(path, "r") as f:
            yield f
        self.status = "processed" if set_status else self.status
        self.processed_at = sqlalchemy.sql.func.now()
        session.commit()

    @property
    def url_parsed(self):
        return urlparse(self.url)


class Article(TimestampedBase):
    __tablename__ = "articles"

    uid = Column(String, default=uid, unique=True)

    title = Column(String, nullable=True)
    published_at = Column(DateTime, nullable=True)

    download_id = Column(Integer, sqlalchemy.ForeignKey("downloads.id"), nullable=True)
    download = sqlalchemy.orm.relationship("Downloads", backref="ai_articles")

    @contextmanager
    def process(self, session, set_status=True):
        path = DOWNLOADS_DIR / self.path
        with open(path, "r") as f:
            yield f
        session.commit()

    @property
    def path(self):
        return self.download.path

    @property
    def url(self):
        return self.download.url


class AiArticles(TimestampedBase):
    __tablename__ = "ai_articles"

    uid = Column(String, default=uid)
    path = Column(String, nullable=True)
    model = Column(String, nullable=True)

    article_id = Column(Integer, sqlalchemy.ForeignKey("articles.id"), nullable=True)
    article = sqlalchemy.orm.relationship("Article", backref="ai_articles")

    query = Column(String, nullable=True)
    response = Column(String, nullable=True)

    status = Column(String, default="pending")

    @property
    def response_json(self):
        return json.loads(self.response)


if __name__ == "__main__":
    Base.metadata.create_all(engine)
