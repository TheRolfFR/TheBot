from sqlalchemy import create_engine, Column, String, Boolean, Integer
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine("sqlite:///app.db")
Base = declarative_base()


class Role(Base):
    __tablename__ = "role"

    name = Column(String, primary_key=True)
    count = Column(Integer)
    color = Column(String)
    is_rank = Column(Boolean)


Base.metadata.create_all(engine)
