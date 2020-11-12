from database import Base
from sqlalchemy import Column, Integer, DateTime, TEXT, String
from datetime import datetime


class Run(Base):
    __tablename__ = 'runs'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now())
    data = Column(TEXT)

    def __init__(self, data):
        self.data = data
