# -*- coding: UTF-8 -*-

from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base


Base = declarative_base(metadata=MetaData(schema='digital_hub_bot'))