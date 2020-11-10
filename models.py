from database import Base
from sqlalchemy import Column, Integer, DateTime, TEXT, String
from datetime import datetime


class Run(Base):
    __tablename__ = 'runs'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now())
    data = Column(TEXT)
    status = Column(String(20))

    def __init__(self,  status, data=None):
        self.data = data
        self.status = status
