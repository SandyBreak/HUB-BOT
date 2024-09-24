# -*- coding: UTF-8 -*-

from sqlalchemy import Column, Integer, BigInteger, String, DateTime
from sqlalchemy.orm import relationship

from .base import Base


class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, nullable=False)
    id_tg = Column(BigInteger, nullable=False)
    nickname = Column(String(length=320), nullable=False)
    fullname = Column(String(length=320), nullable=False)
    date_reg = Column(DateTime, nullable=False)
    id_topic_chat = Column(BigInteger, nullable=True)
