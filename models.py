from database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from datetime import datetime


class Run(Base):
    __tablename__ = 'runs'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now())
    user = Column(String(20))

    def __init__(self, user):
        self.user = user
